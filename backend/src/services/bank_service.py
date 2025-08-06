"""
Bank service for managing bank data, client segmentation, and settlement instruction letters
"""

from typing import Optional, List, Dict, Any
from google.cloud.firestore import DocumentReference
import logging
from datetime import datetime

from config.firebase_config import get_firestore_client
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
        self.db = get_firestore_client()
    
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
    
    async def bank_exists(self, bank_id: str) -> bool:
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
    
    async def get_client_segments(self, bank_id: str) -> List[ClientSegment]:
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
    
    async def get_settlement_letters(self, bank_id: str) -> List[SettlementInstructionLetter]:
        """Get all settlement instruction letters for a bank"""
        try:
            letters_ref = self.db.collection('banks').document(bank_id).collection('settlementInstructionLetters')
            letters_docs = letters_ref.order_by('priority').order_by('rule_name').stream()
            
            letters = []
            for doc in letters_docs:
                letter_data = doc.to_dict()
                letter_data['id'] = doc.id
                letters.append(SettlementInstructionLetter(**letter_data))
            
            return letters
            
        except Exception as e:
            logger.error(f"Error getting settlement letters for bank {bank_id}: {e}")
            return []
    
    async def get_settlement_letter(self, bank_id: str, letter_id: str) -> Optional[SettlementInstructionLetter]:
        """Get specific settlement instruction letter"""
        try:
            letter_doc = (self.db.collection('banks').document(bank_id)
                         .collection('settlementInstructionLetters').document(letter_id).get())
            
            if not letter_doc.exists:
                return None
            
            letter_data = letter_doc.to_dict()
            letter_data['id'] = letter_doc.id
            return SettlementInstructionLetter(**letter_data)
            
        except Exception as e:
            logger.error(f"Error getting settlement letter {letter_id} for bank {bank_id}: {e}")
            return None
    
    async def create_settlement_letter(self, bank_id: str, letter_data: SettlementInstructionLetterCreate, created_by_uid: str) -> Optional[SettlementInstructionLetter]:
        """Create a new settlement instruction letter"""
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
    
    async def update_settlement_letter(self, bank_id: str, letter_id: str, letter_update: SettlementInstructionLetterUpdate, updated_by_uid: str) -> Optional[SettlementInstructionLetter]:
        """Update settlement instruction letter"""
        try:
            letter_ref = (self.db.collection('banks').document(bank_id)
                         .collection('settlementInstructionLetters').document(letter_id))
            
            update_dict = letter_update.model_dump(exclude_unset=True)
            update_dict.update({
                'last_updated_at': datetime.now(),
                'last_updated_by': updated_by_uid
            })
            
            letter_ref.update(update_dict)
            
            return await self.get_settlement_letter(bank_id, letter_id)
            
        except Exception as e:
            logger.error(f"Error updating settlement letter {letter_id} for bank {bank_id}: {e}")
            return None
    
    async def delete_settlement_letter(self, bank_id: str, letter_id: str) -> bool:
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
                segments = await self.get_client_segments(bank_id)
                return {segment.id: [] for segment in segments}
            
            assignments_data = assignments_doc.to_dict()
            current_assignments = assignments_data.get('assignments', {})
            
            # Ensure all segments are represented, even if they have no clients
            segments = await self.get_client_segments(bank_id)
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