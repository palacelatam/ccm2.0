"""
Bank service for managing bank data, client segmentation, and settlement instruction letters
"""

from typing import Optional, List, Dict, Any
from google.cloud.firestore import DocumentReference
from pydantic import ValidationError
import logging
from datetime import datetime
import tempfile
import os
from pathlib import Path
from docx2pdf import convert
from docx import Document
from io import BytesIO

from config.firebase_config import get_cmek_firestore_client
from services.storage_service import StorageService
from models.bank import (
    Bank, BankCreate, BankUpdate,
    ClientSegment, ClientSegmentCreate, ClientSegmentUpdate,
    SettlementInstructionLetter, SettlementInstructionLetterCreate, SettlementInstructionLetterUpdate,
    BankSystemSettings, BankSystemSettingsUpdate,
    ClientSegmentAssignment, BulkClientSegmentAssignment
)

logger = logging.getLogger(__name__)


class BankService:
    """Service for bank management, client segmentation, and settlement letters"""
    
    def __init__(self):
        self.db = get_cmek_firestore_client()
        self.storage_service = StorageService()
    
    # ========== PDF Generation Helper Methods ==========
    
    def _convert_docx_to_pdf(self, docx_content: bytes, temp_filename: str) -> Optional[bytes]:
        """
        Convert DOCX content to PDF using python-docx2pdf library
        
        Args:
            docx_content: The DOCX file content as bytes
            temp_filename: Original filename for temp file creation
            
        Returns:
            PDF content as bytes or None if conversion fails
        """
        temp_dir = None
        
        try:
            # Create temporary directory
            temp_dir = tempfile.mkdtemp()
            
            # Create temporary DOCX file
            docx_filename = os.path.join(temp_dir, temp_filename)
            with open(docx_filename, 'wb') as f:
                f.write(docx_content)
            
            # Expected PDF filename after conversion
            pdf_filename = Path(docx_filename).with_suffix('.pdf')
            
            logger.info(f"Converting DOCX to PDF using python-docx2pdf: {temp_filename}")
            
            # Convert using python-docx2pdf
            convert(docx_filename, str(pdf_filename))
            
            if pdf_filename.exists():
                # Read the generated PDF
                with open(pdf_filename, 'rb') as f:
                    pdf_content = f.read()
                
                logger.info(f"Successfully converted {temp_filename} to PDF ({len(pdf_content)} bytes)")
                return pdf_content
            else:
                logger.error(f"PDF file not generated: {pdf_filename}")
                return None
                
        except Exception as e:
            logger.error(f"Error converting DOCX to PDF using docx2pdf: {e}")
            # Fallback 1: Try mammoth + weasyprint
            try:
                logger.info("Trying mammoth + weasyprint conversion")
                return self._convert_docx_to_pdf_mammoth(docx_content, temp_filename)
            except Exception as mammoth_error:
                logger.error(f"Mammoth conversion failed: {mammoth_error}")
                # Fallback 2: Try reportlab text extraction
                try:
                    logger.info("Trying reportlab text extraction conversion")
                    return self._convert_docx_to_pdf_fallback(docx_content, temp_filename)
                except Exception as fallback_error:
                    logger.error(f"All conversion methods failed: {fallback_error}")
                    return None
        finally:
            # Clean up temporary files
            if temp_dir and os.path.exists(temp_dir):
                try:
                    import shutil
                    shutil.rmtree(temp_dir)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp directory {temp_dir}: {cleanup_error}")
    
    def _convert_docx_to_pdf_fallback(self, docx_content: bytes, temp_filename: str) -> Optional[bytes]:
        """
        Fallback DOCX to PDF conversion using reportlab and python-docx
        This is a basic conversion that extracts text content only
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            from io import BytesIO
            
            logger.info(f"Attempting fallback PDF conversion for {temp_filename}")
            
            # Load DOCX document
            doc = Document(BytesIO(docx_content))
            
            # Create PDF buffer
            pdf_buffer = BytesIO()
            pdf_doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Extract text from DOCX and add to PDF
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    p = Paragraph(paragraph.text, styles['Normal'])
                    story.append(p)
                    story.append(Spacer(1, 12))
            
            # Build PDF
            pdf_doc.build(story)
            pdf_content = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            logger.info(f"Fallback conversion successful for {temp_filename} ({len(pdf_content)} bytes)")
            return pdf_content
            
        except Exception as e:
            logger.error(f"Fallback PDF conversion failed: {e}")
            return None
    
    def _convert_docx_to_pdf_mammoth(self, docx_content: bytes, temp_filename: str) -> Optional[bytes]:
        """
        Convert DOCX to PDF using mammoth (DOCX to HTML) + weasyprint (HTML to PDF)
        This preserves more formatting than the reportlab fallback
        """
        try:
            import mammoth
            import weasyprint
            from io import BytesIO
            
            logger.info(f"Converting DOCX to HTML using mammoth: {temp_filename}")
            
            # Convert DOCX to HTML using mammoth
            with BytesIO(docx_content) as docx_stream:
                result = mammoth.convert_to_html(docx_stream)
                html_content = result.value
            
            if result.messages:
                logger.warning(f"Mammoth conversion warnings: {result.messages}")
            
            # Create basic HTML document with styling
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
                    p {{ margin-bottom: 10px; }}
                    h1, h2, h3 {{ color: #333; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            logger.info(f"Converting HTML to PDF using weasyprint: {temp_filename}")
            
            # Convert HTML to PDF using weasyprint
            pdf_bytes = weasyprint.HTML(string=full_html).write_pdf()
            
            logger.info(f"Mammoth conversion successful for {temp_filename} ({len(pdf_bytes)} bytes)")
            return pdf_bytes
            
        except Exception as e:
            logger.error(f"Mammoth PDF conversion failed: {e}")
            return None
    
    async def _generate_pdf_preview(
        self,
        file_content: bytes,
        filename: str,
        bank_id: str,
        segment_id: str,
        uploaded_by: str
    ) -> Optional[Dict[str, Any]]:
        """
        Generate PDF preview from DOCX template and upload to Cloud Storage
        
        Returns:
            Upload result dictionary or None if generation/upload fails
        """
        try:
            # Convert DOCX to PDF
            pdf_content = self._convert_docx_to_pdf(file_content, filename)
            
            if not pdf_content:
                logger.warning(f"Failed to generate PDF preview for {filename}")
                return None
            
            # Generate PDF filename
            pdf_filename = Path(filename).with_suffix('.pdf').name
            
            # Upload PDF to Cloud Storage
            pdf_upload_result = await self.storage_service.upload_settlement_document(
                file_content=pdf_content,
                filename=pdf_filename,
                content_type="application/pdf",
                bank_id=bank_id,
                segment_id=segment_id,
                uploaded_by=uploaded_by
            )
            
            if pdf_upload_result["success"]:
                logger.info(f"Successfully uploaded PDF preview: {pdf_upload_result['storage_path']}")
                return pdf_upload_result
            else:
                logger.error(f"Failed to upload PDF preview: {pdf_upload_result.get('error')}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating PDF preview for {filename}: {e}")
            return None
    
    # ========== Bank Management Methods ==========
    
    async def get_bank(self, bank_id: str) -> Optional[Bank]:
        """Get bank by ID"""
        try:
            bank_doc = self.db.collection('banks').document(bank_id).get()
            
            if not bank_doc.exists:
                logger.warning(f"Bank {bank_id} not found")
                return None
            
            bank_data = bank_doc.to_dict()
            bank_data['id'] = bank_doc.id
            return Bank(**bank_data)
            
        except Exception as e:
            logger.error(f"Error getting bank {bank_id}: {e}")
            return None
    
    def bank_exists(self, bank_id: str) -> bool:
        """Check if bank exists"""
        try:
            bank_doc = self.db.collection('banks').document(bank_id).get()
            return bank_doc.exists
        except Exception as e:
            logger.error(f"Error checking if bank {bank_id} exists: {e}")
            return False
    
    async def create_bank(self, bank_data: BankCreate, created_by_uid: str) -> Optional[Bank]:
        """Create a new bank"""
        try:
            bank_ref = self.db.collection('banks').document()
            
            bank_dict = bank_data.model_dump()
            bank_dict.update({
                'id': bank_ref.id,
                'created_at': datetime.now(),
                'last_updated_at': datetime.now(),
                'last_updated_by': created_by_uid
            })
            
            bank_ref.set(bank_dict)
            
            return Bank(**bank_dict)
            
        except Exception as e:
            logger.error(f"Error creating bank: {e}")
            return None
    
    async def update_bank(self, bank_id: str, bank_update: BankUpdate, updated_by_uid: str) -> Optional[Bank]:
        """Update bank information"""
        try:
            bank_ref = self.db.collection('banks').document(bank_id)
            
            # Check if bank exists
            if not (await self.bank_exists(bank_id)):
                logger.warning(f"Bank {bank_id} not found for update")
                return None
            
            update_dict = bank_update.model_dump(exclude_unset=True)
            update_dict.update({
                'last_updated_at': datetime.now(),
                'last_updated_by': updated_by_uid
            })
            
            bank_ref.update(update_dict)
            
            # Return updated bank
            return await self.get_bank(bank_id)
            
        except Exception as e:
            logger.error(f"Error updating bank {bank_id}: {e}")
            return None
    
    # ========== Client Segmentation Methods ==========
    
    def get_client_segments(self, bank_id: str) -> List[ClientSegment]:
        """Get all client segments for a bank"""
        try:
            segments_ref = self.db.collection('banks').document(bank_id).collection('clientSegments')
            segments_docs = segments_ref.stream()
            
            segments = []
            for doc in segments_docs:
                segment_data = doc.to_dict()
                segment_data['id'] = doc.id
                segments.append(ClientSegment(**segment_data))
            
            return segments
            
        except Exception as e:
            logger.error(f"Error getting client segments for bank {bank_id}: {e}")
            return []
    
    async def get_client_segment(self, bank_id: str, segment_id: str) -> Optional[ClientSegment]:
        """Get specific client segment"""
        try:
            segment_doc = (self.db.collection('banks').document(bank_id)
                          .collection('clientSegments').document(segment_id).get())
            
            if not segment_doc.exists:
                return None
            
            segment_data = segment_doc.to_dict()
            segment_data['id'] = segment_doc.id
            return ClientSegment(**segment_data)
            
        except Exception as e:
            logger.error(f"Error getting client segment {segment_id} for bank {bank_id}: {e}")
            return None
    
    async def create_client_segment(self, bank_id: str, segment_data: ClientSegmentCreate, created_by_uid: str) -> Optional[ClientSegment]:
        """Create a new client segment"""
        try:
            segments_ref = self.db.collection('banks').document(bank_id).collection('clientSegments')
            segment_ref = segments_ref.document()
            
            segment_dict = segment_data.model_dump()
            segment_dict.update({
                'id': segment_ref.id,
                'created_at': datetime.now(),
                'last_updated_at': datetime.now(),
                'last_updated_by': created_by_uid
            })
            
            segment_ref.set(segment_dict)
            
            return ClientSegment(**segment_dict)
            
        except Exception as e:
            logger.error(f"Error creating client segment for bank {bank_id}: {e}")
            return None
    
    async def update_client_segment(self, bank_id: str, segment_id: str, segment_update: ClientSegmentUpdate, updated_by_uid: str) -> Optional[ClientSegment]:
        """Update client segment"""
        try:
            segment_ref = (self.db.collection('banks').document(bank_id)
                          .collection('clientSegments').document(segment_id))
            
            update_dict = segment_update.model_dump(exclude_unset=True)
            update_dict.update({
                'last_updated_at': datetime.now(),
                'last_updated_by': updated_by_uid
            })
            
            segment_ref.update(update_dict)
            
            return await self.get_client_segment(bank_id, segment_id)
            
        except Exception as e:
            logger.error(f"Error updating client segment {segment_id} for bank {bank_id}: {e}")
            return None
    
    async def delete_client_segment(self, bank_id: str, segment_id: str) -> bool:
        """Delete client segment"""
        try:
            segment_ref = (self.db.collection('banks').document(bank_id)
                          .collection('clientSegments').document(segment_id))
            segment_ref.delete()
            
            logger.info(f"Deleted client segment {segment_id} for bank {bank_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting client segment {segment_id} for bank {bank_id}: {e}")
            return False
    
    # ========== Settlement Instruction Letters Methods ==========
    
    def get_settlement_letters(self, bank_id: str) -> List[SettlementInstructionLetter]:
        """Get all settlement instruction letters for a bank"""
        try:
            letters_ref = self.db.collection('banks').document(bank_id).collection('settlementInstructionLetters')
            letters_docs = letters_ref.stream()
            
            letters = []
            for doc in letters_docs:
                letter_data = doc.to_dict()
                letter_data['id'] = doc.id
                
                # Handle DocumentReference objects - convert them to strings
                if 'clientSegmentId' in letter_data:
                    if hasattr(letter_data['clientSegmentId'], 'path'):
                        # It's a DocumentReference, get the ID from the path
                        letter_data['clientSegmentId'] = letter_data['clientSegmentId'].path.split('/')[-1]
                
                if 'lastUpdatedBy' in letter_data:
                    if hasattr(letter_data['lastUpdatedBy'], 'path'):
                        # It's a DocumentReference, get the ID from the path
                        letter_data['lastUpdatedBy'] = letter_data['lastUpdatedBy'].path.split('/')[-1]
                
                # Handle field name mapping from database (camelCase) to model (snake_case)
                if 'ruleName' in letter_data:
                    letter_data['rule_name'] = letter_data['ruleName']
                
                letters.append(SettlementInstructionLetter(**letter_data))
            
            return letters
            
        except Exception as e:
            logger.error(f"Error getting settlement letters for bank {bank_id}: {e}")
            return []
    
    def get_settlement_letter(self, bank_id: str, letter_id: str) -> Optional[SettlementInstructionLetter]:
        """Get specific settlement instruction letter"""
        try:
            letter_doc = (self.db.collection('banks').document(bank_id)
                         .collection('settlementInstructionLetters').document(letter_id).get())
            
            if not letter_doc.exists:
                return None
            
            letter_data = letter_doc.to_dict()
            letter_data['id'] = letter_doc.id
            
            # Handle DocumentReference objects - convert them to strings
            if 'clientSegmentId' in letter_data:
                if hasattr(letter_data['clientSegmentId'], 'path'):
                    letter_data['clientSegmentId'] = letter_data['clientSegmentId'].path.split('/')[-1]
            
            if 'lastUpdatedBy' in letter_data:
                if hasattr(letter_data['lastUpdatedBy'], 'path'):
                    letter_data['lastUpdatedBy'] = letter_data['lastUpdatedBy'].path.split('/')[-1]
            
            try:
                return SettlementInstructionLetter(**letter_data)
            except ValidationError as ve:
                logger.error(f"Validation error creating SettlementInstructionLetter from data {letter_data}: {ve}")
                return None
            
        except Exception as e:
            logger.error(f"Error getting settlement letter {letter_id} for bank {bank_id}: {e}")
            return None
    
    def create_settlement_letter(self, bank_id: str, letter_data: SettlementInstructionLetterCreate, created_by_uid: str) -> Optional[SettlementInstructionLetter]:
        """Create a new settlement instruction letter (without file upload)"""
        try:
            letters_ref = self.db.collection('banks').document(bank_id).collection('settlementInstructionLetters')
            letter_ref = letters_ref.document()
            
            letter_dict = letter_data.model_dump()
            letter_dict.update({
                'id': letter_ref.id,
                'created_at': datetime.now(),
                'last_updated_at': datetime.now(),
                'last_updated_by': created_by_uid
            })
            
            letter_ref.set(letter_dict)
            
            return SettlementInstructionLetter(**letter_dict)
            
        except Exception as e:
            logger.error(f"Error creating settlement letter for bank {bank_id}: {e}")
            return None

    async def create_settlement_letter_with_document(
        self, 
        bank_id: str, 
        letter_data: SettlementInstructionLetterCreate, 
        file_content: bytes,
        filename: str,
        content_type: str,
        created_by_uid: str
    ) -> Optional[SettlementInstructionLetter]:
        """Create a new settlement instruction letter with document upload and PDF preview generation"""
        try:
            # First, upload the DOCX document to Cloud Storage
            segment_id = letter_data.client_segment_id if letter_data.client_segment_id else "default"
            
            docx_upload_result = await self.storage_service.upload_settlement_document(
                file_content=file_content,
                filename=filename,
                content_type=content_type,
                bank_id=bank_id,
                segment_id=segment_id,
                uploaded_by=created_by_uid
            )
            
            if not docx_upload_result["success"]:
                logger.error(f"Failed to upload DOCX document: {docx_upload_result.get('error')}")
                return None
            
            # Generate PDF preview for browser viewing
            pdf_upload_result = await self._generate_pdf_preview(
                file_content=file_content,
                filename=filename,
                bank_id=bank_id,
                segment_id=segment_id,
                uploaded_by=created_by_uid
            )
            
            # Create the settlement letter record with document info
            letters_ref = self.db.collection('banks').document(bank_id).collection('settlementInstructionLetters')
            letter_ref = letters_ref.document()
            
            letter_dict = letter_data.model_dump()
            letter_dict.update({
                'id': letter_ref.id,
                # DOCX document storage information (for download/processing)
                'document_name': filename,
                'document_storage_path': docx_upload_result["storage_path"],
                'document_url': docx_upload_result["public_url"],
                'document_size': docx_upload_result["file_size"],
                'document_content_type': content_type,
                'document_uploaded_at': docx_upload_result["uploaded_at"],
                # PDF preview information (for browser preview)
                'has_pdf_preview': pdf_upload_result is not None,
                'pdf_preview_storage_path': pdf_upload_result.get("storage_path") if pdf_upload_result else None,
                'pdf_preview_url': pdf_upload_result.get("public_url") if pdf_upload_result else None,
                # Standard metadata
                'created_at': datetime.now(),
                'last_updated_at': datetime.now(),
                'last_updated_by': created_by_uid
            })
            
            letter_ref.set(letter_dict)
            
            logger.info(f"Created settlement letter {letter_ref.id} with document {docx_upload_result['storage_path']}")
            if pdf_upload_result:
                logger.info(f"PDF preview available at {pdf_upload_result['storage_path']}")
            else:
                logger.warning(f"PDF preview generation failed for {filename}")
            
            return SettlementInstructionLetter(**letter_dict)
            
        except Exception as e:
            logger.error(f"Error creating settlement letter with document for bank {bank_id}: {e}")
            return None
    
    def update_settlement_letter(self, bank_id: str, letter_id: str, letter_update: SettlementInstructionLetterUpdate, updated_by_uid: str) -> Optional[SettlementInstructionLetter]:
        """Update settlement instruction letter"""
        try:
            letter_ref = (self.db.collection('banks').document(bank_id)
                         .collection('settlementInstructionLetters').document(letter_id))
            
            update_dict = letter_update.model_dump(exclude_unset=True, exclude_none=False)
            update_dict.update({
                'last_updated_at': datetime.now(),
                'last_updated_by': updated_by_uid
            })
            
            letter_ref.update(update_dict)
            
            return self.get_settlement_letter(bank_id, letter_id)
            
        except Exception as e:
            logger.error(f"Error updating settlement letter {letter_id} for bank {bank_id}: {e}")
            return None

    async def update_settlement_letter_with_document(
        self, 
        bank_id: str, 
        letter_id: str,
        letter_update: SettlementInstructionLetterUpdate,
        file_content: bytes,
        filename: str,
        content_type: str,
        updated_by_uid: str
    ) -> Optional[SettlementInstructionLetter]:
        """Update settlement instruction letter with document replacement"""
        try:
            # Get current letter to check for existing document
            current_letter = self.get_settlement_letter(bank_id, letter_id)
            if current_letter is None:
                logger.error(f"Settlement letter {letter_id} not found for update with document")
                return None
            
            # If there's an existing document, delete it first
            old_storage_path = getattr(current_letter, 'document_storage_path', None)
            if old_storage_path:
                try:
                    delete_result = await self.storage_service.delete_settlement_document(old_storage_path)
                    if not delete_result["success"]:
                        logger.warning(f"Failed to delete old document {old_storage_path}: {delete_result.get('error')}")
                    else:
                        logger.info(f"Successfully deleted old document {old_storage_path}")
                except Exception as delete_error:
                    logger.warning(f"Error deleting old document {old_storage_path}: {delete_error}")
            
            # Upload the new document to Cloud Storage
            segment_id = letter_update.client_segment_id if letter_update.client_segment_id else current_letter.client_segment_id or "default"
            
            upload_result = await self.storage_service.upload_settlement_document(
                file_content=file_content,
                filename=filename,
                content_type=content_type,
                bank_id=bank_id,
                segment_id=segment_id,
                uploaded_by=updated_by_uid
            )
            
            if not upload_result["success"]:
                logger.error(f"Failed to upload new document: {upload_result.get('error')}")
                return None
            
            # Update the letter with new document information
            letter_ref = (self.db.collection('banks').document(bank_id)
                         .collection('settlementInstructionLetters').document(letter_id))
            
            update_dict = letter_update.model_dump(exclude_unset=True, exclude_none=False)
            update_dict.update({
                # New document storage information
                'document_name': filename,
                'document_storage_path': upload_result["storage_path"],
                'document_url': upload_result["public_url"],
                'document_size': upload_result["file_size"],
                'document_content_type': content_type,
                'document_uploaded_at': upload_result["uploaded_at"],
                # Standard metadata
                'last_updated_at': datetime.now(),
                'last_updated_by': updated_by_uid
            })
            
            letter_ref.update(update_dict)
            
            logger.info(f"Updated settlement letter {letter_id} with new document {upload_result['storage_path']}")
            
            return self.get_settlement_letter(bank_id, letter_id)
            
        except Exception as e:
            logger.error(f"Error updating settlement letter {letter_id} with document for bank {bank_id}: {e}")
            return None
    
    def delete_settlement_letter(self, bank_id: str, letter_id: str) -> bool:
        """Delete settlement instruction letter"""
        try:
            letter_ref = (self.db.collection('banks').document(bank_id)
                         .collection('settlementInstructionLetters').document(letter_id))
            letter_ref.delete()
            
            logger.info(f"Deleted settlement letter {letter_id} for bank {bank_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting settlement letter {letter_id} for bank {bank_id}: {e}")
            return False
    
    # ========== Bank System Settings Methods ==========
    
    async def get_bank_system_settings(self, bank_id: str) -> Optional[BankSystemSettings]:
        """Get bank system settings"""
        try:
            settings_doc = (self.db.collection('banks').document(bank_id)
                           .collection('systemSettings').document('configuration').get())
            
            if not settings_doc.exists:
                logger.info(f"No system settings found for bank {bank_id}, returning defaults")
                return BankSystemSettings()
            
            settings_data = settings_doc.to_dict()
            return BankSystemSettings(**settings_data)
            
        except Exception as e:
            logger.error(f"Error getting bank system settings for {bank_id}: {e}")
            return None
    
    async def update_bank_system_settings(self, bank_id: str, settings_update: BankSystemSettingsUpdate, updated_by_uid: str) -> Optional[BankSystemSettings]:
        """Update bank system settings"""
        try:
            settings_ref = (self.db.collection('banks').document(bank_id)
                           .collection('systemSettings').document('configuration'))
            
            update_dict = settings_update.model_dump(exclude_unset=True)
            update_dict.update({
                'last_updated_at': datetime.now(),
                'last_updated_by': updated_by_uid
            })
            
            settings_ref.set(update_dict, merge=True)
            
            return await self.get_bank_system_settings(bank_id)
            
        except Exception as e:
            logger.error(f"Error updating bank system settings for {bank_id}: {e}")
            return None
    
    # ========== Client Assignment Methods ==========
    
    async def assign_client_to_segment(self, bank_id: str, client_id: str, segment_id: str, assigned_by_uid: str) -> bool:
        """Assign a client to a segment"""
        try:
            # Get the current assignments document
            assignments_ref = (self.db.collection('banks').document(bank_id)
                             .collection('clientSegmentAssignments').document('assignments'))
            
            assignments_doc = assignments_ref.get()
            
            if assignments_doc.exists:
                assignments_data = assignments_doc.to_dict()
                current_assignments = assignments_data.get('assignments', {})
            else:
                current_assignments = {}
            
            # Remove client from any existing segment
            for seg_id, client_ids in current_assignments.items():
                if client_id in client_ids:
                    client_ids.remove(client_id)
            
            # Add client to new segment
            if segment_id not in current_assignments:
                current_assignments[segment_id] = []
            
            if client_id not in current_assignments[segment_id]:
                current_assignments[segment_id].append(client_id)
            
            # Update the document
            assignments_ref.set({
                'assignments': current_assignments,
                'lastUpdatedAt': datetime.now(),
                'lastUpdatedBy': assigned_by_uid
            })
            
            logger.info(f"Assigned client {client_id} to segment {segment_id} in bank {bank_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning client {client_id} to segment {segment_id} in bank {bank_id}: {e}")
            return False
    
    async def remove_client_from_segment(self, bank_id: str, client_id: str, segment_id: str) -> bool:
        """Remove a client from a segment"""
        try:
            # Get the current assignments document
            assignments_ref = (self.db.collection('banks').document(bank_id)
                             .collection('clientSegmentAssignments').document('assignments'))
            
            assignments_doc = assignments_ref.get()
            
            if not assignments_doc.exists:
                logger.warning(f"No assignments found for bank {bank_id}")
                return False
            
            assignments_data = assignments_doc.to_dict()
            current_assignments = assignments_data.get('assignments', {})
            
            # Remove client from the specified segment
            if segment_id in current_assignments and client_id in current_assignments[segment_id]:
                current_assignments[segment_id].remove(client_id)
                
                # Update the document
                assignments_ref.set({
                    'assignments': current_assignments,
                    'lastUpdatedAt': datetime.now()
                })
                
                logger.info(f"Removed client {client_id} from segment {segment_id} in bank {bank_id}")
                return True
            else:
                logger.warning(f"Client {client_id} not found in segment {segment_id} for bank {bank_id}")
                return False
            
        except Exception as e:
            logger.error(f"Error removing client {client_id} from segment {segment_id} in bank {bank_id}: {e}")
            return False
    
    async def get_clients_in_segment(self, bank_id: str, segment_id: str) -> List[str]:
        """Get all client IDs assigned to a segment"""
        try:
            assignments_ref = (self.db.collection('banks').document(bank_id)
                             .collection('clientSegmentAssignments').document('assignments'))
            
            assignments_doc = assignments_ref.get()
            
            if not assignments_doc.exists:
                return []
            
            assignments_data = assignments_doc.to_dict()
            current_assignments = assignments_data.get('assignments', {})
            
            return current_assignments.get(segment_id, [])
            
        except Exception as e:
            logger.error(f"Error getting clients in segment {segment_id} for bank {bank_id}: {e}")
            return []
    
    async def get_client_segment_assignments(self, bank_id: str) -> Dict[str, List[str]]:
        """Get all client-segment assignments for a bank"""
        try:
            assignments_ref = (self.db.collection('banks').document(bank_id)
                             .collection('clientSegmentAssignments').document('assignments'))
            
            assignments_doc = assignments_ref.get()
            
            if not assignments_doc.exists:
                # Return empty assignments for all segments
                segments = self.get_client_segments(bank_id)
                return {segment.id: [] for segment in segments}
            
            assignments_data = assignments_doc.to_dict()
            current_assignments = assignments_data.get('assignments', {})
            
            # Ensure all segments are represented, even if they have no clients
            segments = self.get_client_segments(bank_id)
            result = {}
            for segment in segments:
                result[segment.id] = current_assignments.get(segment.id, [])
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting client segment assignments for bank {bank_id}: {e}")
            return {}
    
    async def bulk_assign_clients_to_segments(self, bank_id: str, assignments: BulkClientSegmentAssignment, assigned_by_uid: str) -> bool:
        """Bulk assign clients to segments"""
        try:
            # Get the current assignments document
            assignments_ref = (self.db.collection('banks').document(bank_id)
                             .collection('clientSegmentAssignments').document('assignments'))
            
            assignments_doc = assignments_ref.get()
            
            if assignments_doc.exists:
                assignments_data = assignments_doc.to_dict()
                current_assignments = assignments_data.get('assignments', {})
            else:
                current_assignments = {}
            
            # Process each assignment
            for assignment in assignments.assignments:
                client_id = assignment.client_id
                segment_id = assignment.segment_id
                
                # Remove client from any existing segment
                for seg_id, client_ids in current_assignments.items():
                    if client_id in client_ids:
                        client_ids.remove(client_id)
                
                # Add client to new segment
                if segment_id not in current_assignments:
                    current_assignments[segment_id] = []
                
                if client_id not in current_assignments[segment_id]:
                    current_assignments[segment_id].append(client_id)
            
            # Update the document
            assignments_ref.set({
                'assignments': current_assignments,
                'lastUpdatedAt': datetime.now(),
                'lastUpdatedBy': assigned_by_uid
            })
            
            logger.info(f"Bulk assigned {len(assignments.assignments)} clients to segments in bank {bank_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error bulk assigning clients to segments in bank {bank_id}: {e}")
            return False
    
    # ========== Client Management Methods ==========
    
    async def get_all_clients(self) -> List[Dict[str, Any]]:
        """Get all clients (independent of banks)"""
        try:
            clients_docs = self.db.collection('clients').stream()
            
            clients = []
            for doc in clients_docs:
                client_data = doc.to_dict()
                client_data['id'] = doc.id
                clients.append(client_data)
            
            logger.info(f"Found {len(clients)} clients")
            return clients
            
        except Exception as e:
            logger.error(f"Error getting all clients: {e}")
            return []