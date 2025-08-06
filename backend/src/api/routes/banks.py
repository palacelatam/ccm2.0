"""
Bank management routes
"""

from fastapi import APIRouter, Request, HTTPException, status, Path, Query, File, UploadFile, Form
from typing import List, Dict, Any
import logging

from api.middleware.auth_middleware import get_auth_context, require_permission
from services.bank_service import BankService
from models.base import APIResponse
from models.bank import (
    Bank, BankCreate, BankUpdate,
    ClientSegment, ClientSegmentCreate, ClientSegmentUpdate,
    SettlementInstructionLetter, SettlementInstructionLetterCreate, SettlementInstructionLetterUpdate,
    BankSystemSettings, BankSystemSettingsUpdate,
    ClientSegmentAssignment, BulkClientSegmentAssignment
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/banks", tags=["banks"])


def validate_bank_access(auth_context, bank_id: str):
    """Validate user has access to the specified bank"""
    if auth_context.organization_type != "bank" or auth_context.organization_id != bank_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this bank"
        )


# ========== Bank Management Endpoints ==========

@router.get("/{bank_id}", response_model=APIResponse[Bank])
@require_permission("manage_bank_settings")
async def get_bank(
    request: Request,
    bank_id: str = Path(..., description="Bank ID")
):
    """Get bank information"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    bank = await bank_service.get_bank(bank_id)
    
    if bank is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    return APIResponse(
        success=True,
        data=bank,
        message="Bank retrieved successfully"
    )


@router.put("/{bank_id}", response_model=APIResponse[Bank])
@require_permission("manage_bank_settings")
async def update_bank(
    request: Request,
    bank_update: BankUpdate,
    bank_id: str = Path(..., description="Bank ID")
):
    """Update bank information"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    updated_bank = await bank_service.update_bank(
        bank_id, bank_update, auth_context.uid
    )
    
    if updated_bank is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found or failed to update"
        )
    
    return APIResponse(
        success=True,
        data=updated_bank,
        message="Bank updated successfully"
    )


# ========== Client Segmentation Endpoints ==========

@router.get("/{bank_id}/client-segments", response_model=APIResponse[List[ClientSegment]])
@require_permission("manage_client_segments")
async def get_client_segments(
    request: Request,
    bank_id: str = Path(..., description="Bank ID")
):
    """Get all client segments for a bank"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    segments = bank_service.get_client_segments(bank_id)
    
    return APIResponse(
        success=True,
        data=segments,
        message="Client segments retrieved successfully"
    )


@router.get("/{bank_id}/client-segments/{segment_id}", response_model=APIResponse[ClientSegment])
@require_permission("manage_client_segments")
async def get_client_segment(
    request: Request,
    bank_id: str = Path(..., description="Bank ID"),
    segment_id: str = Path(..., description="Segment ID")
):
    """Get specific client segment"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    segment = await bank_service.get_client_segment(bank_id, segment_id)
    
    if segment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client segment not found"
        )
    
    return APIResponse(
        success=True,
        data=segment,
        message="Client segment retrieved successfully"
    )


@router.post("/{bank_id}/client-segments", response_model=APIResponse[ClientSegment])
@require_permission("manage_client_segments")
async def create_client_segment(
    request: Request,
    segment_data: ClientSegmentCreate,
    bank_id: str = Path(..., description="Bank ID")
):
    """Create a new client segment"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    created_segment = await bank_service.create_client_segment(
        bank_id, segment_data, auth_context.uid
    )
    
    if created_segment is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create client segment"
        )
    
    return APIResponse(
        success=True,
        data=created_segment,
        message="Client segment created successfully"
    )


@router.put("/{bank_id}/client-segments/{segment_id}", response_model=APIResponse[ClientSegment])
@require_permission("manage_client_segments")
async def update_client_segment(
    request: Request,
    segment_update: ClientSegmentUpdate,
    bank_id: str = Path(..., description="Bank ID"),
    segment_id: str = Path(..., description="Segment ID")
):
    """Update client segment"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    updated_segment = await bank_service.update_client_segment(
        bank_id, segment_id, segment_update, auth_context.uid
    )
    
    if updated_segment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client segment not found or failed to update"
        )
    
    return APIResponse(
        success=True,
        data=updated_segment,
        message="Client segment updated successfully"
    )


@router.delete("/{bank_id}/client-segments/{segment_id}", response_model=APIResponse[dict])
@require_permission("manage_client_segments")
async def delete_client_segment(
    request: Request,
    bank_id: str = Path(..., description="Bank ID"),
    segment_id: str = Path(..., description="Segment ID")
):
    """Delete client segment"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    success = await bank_service.delete_client_segment(bank_id, segment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client segment not found or failed to delete"
        )
    
    return APIResponse(
        success=True,
        data={},
        message="Client segment deleted successfully"
    )


# ========== Settlement Instruction Letters Endpoints ==========

@router.get("/{bank_id}/settlement-letters", response_model=APIResponse[List[SettlementInstructionLetter]])
@require_permission("manage_instruction_letters")
async def get_settlement_letters(
    request: Request,
    bank_id: str = Path(..., description="Bank ID")
):
    """Get all settlement instruction letters for a bank"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    letters = bank_service.get_settlement_letters(bank_id)
    
    return APIResponse(
        success=True,
        data=letters,
        message="Settlement letters retrieved successfully"
    )


@router.get("/{bank_id}/settlement-letters/{letter_id}/document/preview", response_model=APIResponse[dict])
@require_permission("manage_instruction_letters")
async def preview_settlement_letter_document(
    request: Request,
    bank_id: str = Path(..., description="Bank ID"),
    letter_id: str = Path(..., description="Letter ID"),
    expiration_minutes: int = Query(60, description="Signed URL expiration in minutes", ge=1, le=1440)
):
    """Generate a signed URL for previewing the settlement letter document"""
    try:
        auth_context = get_auth_context(request)
        validate_bank_access(auth_context, bank_id)
        
        bank_service = BankService()
        
        # Get the settlement letter to retrieve the document storage path
        letter = bank_service.get_settlement_letter(bank_id, letter_id)
        if letter is None:
            return APIResponse(
                success=False,
                data={},
                message="Settlement letter not found"
            )
        
        # Check if the letter has a document_storage_path
        storage_path = getattr(letter, 'document_storage_path', None)
        
        if not storage_path:
            return APIResponse(
                success=False,
                data={},
                message="No document storage path found for this settlement letter"
            )
        
        try:
            # Generate signed URL for document preview
            storage_service = bank_service.storage_service
            signed_url_result = await storage_service.generate_document_signed_url(
                storage_path, 
                expiration_minutes
            )
            
            if not signed_url_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to generate preview URL: {signed_url_result.get('error', 'Unknown error')}"
                )
            
            return APIResponse(
                success=True,
                data={
                    "signed_url": signed_url_result["signed_url"],
                    "expires_in_minutes": signed_url_result["expires_in_minutes"],
                    "document_name": getattr(letter, 'document_name', 'settlement_document.pdf')
                },
                message="Document preview URL generated successfully"
            )
            
        except Exception as signed_url_error:
            logger.error(f"Error generating signed URL for {storage_path}: {signed_url_error}")
            return APIResponse(
                success=False,
                data={},
                message=f"Failed to generate signed URL: {str(signed_url_error)}"
            )
        
    except Exception as e:
        logger.error(f"Error in preview endpoint: {e}")
        return APIResponse(
            success=False,
            data={},
            message=f"Error: {str(e)}"
        )


@router.get("/{bank_id}/settlement-letters/{letter_id}", response_model=APIResponse[SettlementInstructionLetter])
@require_permission("manage_instruction_letters")
async def get_settlement_letter(
    request: Request,
    bank_id: str = Path(..., description="Bank ID"),
    letter_id: str = Path(..., description="Letter ID")
):
    """Get specific settlement instruction letter"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    letter = bank_service.get_settlement_letter(bank_id, letter_id)
    
    if letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement letter not found"
        )
    
    return APIResponse(
        success=True,
        data=letter,
        message="Settlement letter retrieved successfully"
    )


@router.post("/{bank_id}/settlement-letters", response_model=APIResponse[SettlementInstructionLetter])
@require_permission("manage_instruction_letters")
async def create_settlement_letter(
    request: Request,
    letter_data: SettlementInstructionLetterCreate,
    bank_id: str = Path(..., description="Bank ID")
):
    """Create a new settlement instruction letter (without file upload)"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    created_letter = bank_service.create_settlement_letter(
        bank_id, letter_data, auth_context.uid
    )
    
    if created_letter is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create settlement letter"
        )
    
    return APIResponse(
        success=True,
        data=created_letter,
        message="Settlement letter created successfully"
    )


@router.post("/{bank_id}/settlement-letters/with-document", response_model=APIResponse[SettlementInstructionLetter])
@require_permission("manage_instruction_letters")
async def create_settlement_letter_with_document(
    request: Request,
    bank_id: str = Path(..., description="Bank ID"),
    # Form fields for the letter data
    rule_name: str = Form(..., description="Settlement instruction rule name"),
    product: str = Form(..., description="Product type"),
    client_segment_id: str = Form(None, description="Client segment ID"),
    priority: int = Form(1, description="Priority order"),
    active: bool = Form(True, description="Whether the letter is active"),
    template_variables: str = Form("[]", description="JSON array of template variables"),
    conditions: str = Form("{}", description="JSON object of conditions"),
    # File upload
    document: UploadFile = File(..., description="PDF document to upload")
):
    """Create a new settlement instruction letter with document upload"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    # Validate file type
    if document.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    
    try:
        # Read file content
        file_content = await document.read()
        
        # Parse JSON fields
        import json
        try:
            template_variables_list = json.loads(template_variables) if template_variables else []
            conditions_dict = json.loads(conditions) if conditions else {}
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON format: {str(e)}"
            )
        
        # Create settlement letter data object
        letter_data = SettlementInstructionLetterCreate(
            rule_name=rule_name,
            product=product,
            client_segment_id=client_segment_id,
            priority=priority,
            active=active,
            document_name=document.filename,
            document_url="",  # Will be set by the service
            template_variables=template_variables_list,
            conditions=conditions_dict
        )
        
        # Create letter with document
        created_letter = await bank_service.create_settlement_letter_with_document(
            bank_id=bank_id,
            letter_data=letter_data,
            file_content=file_content,
            filename=document.filename,
            content_type=document.content_type,
            created_by_uid=auth_context.uid
        )
        
        if created_letter is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create settlement letter with document"
            )
        
        return APIResponse(
            success=True,
            data=created_letter,
            message="Settlement letter with document created successfully"
        )
        
    except Exception as e:
        logger.error(f"Error creating settlement letter with document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while creating settlement letter"
        )


@router.put("/{bank_id}/settlement-letters/{letter_id}", response_model=APIResponse[SettlementInstructionLetter])
@require_permission("manage_instruction_letters")
async def update_settlement_letter(
    request: Request,
    letter_update: SettlementInstructionLetterUpdate,
    bank_id: str = Path(..., description="Bank ID"),
    letter_id: str = Path(..., description="Letter ID")
):
    """Update settlement instruction letter"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    updated_letter = bank_service.update_settlement_letter(
        bank_id, letter_id, letter_update, auth_context.uid
    )
    
    if updated_letter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement letter not found or failed to update"
        )
    
    return APIResponse(
        success=True,
        data=updated_letter,
        message="Settlement letter updated successfully"
    )


@router.delete("/{bank_id}/settlement-letters/{letter_id}", response_model=APIResponse[dict])
@require_permission("manage_instruction_letters")
async def delete_settlement_letter(
    request: Request,
    bank_id: str = Path(..., description="Bank ID"),
    letter_id: str = Path(..., description="Letter ID")
):
    """Delete settlement instruction letter"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    success = bank_service.delete_settlement_letter(bank_id, letter_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement letter not found or failed to delete"
        )
    
    return APIResponse(
        success=True,
        data={},
        message="Settlement letter deleted successfully"
    )



# ========== Client Segment Assignment Endpoints ==========

@router.get("/{bank_id}/client-assignments", response_model=APIResponse[Dict[str, List[str]]])
@require_permission("manage_client_segments")
async def get_client_segment_assignments(
    request: Request,
    bank_id: str = Path(..., description="Bank ID")
):
    """Get all client-segment assignments for a bank"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    assignments = await bank_service.get_client_segment_assignments(bank_id)
    
    return APIResponse(
        success=True,
        data=assignments,
        message="Client segment assignments retrieved successfully"
    )


@router.post("/{bank_id}/client-assignments/assign", response_model=APIResponse[dict])
@require_permission("manage_client_segments")
async def assign_client_to_segment(
    request: Request,
    assignment: ClientSegmentAssignment,
    bank_id: str = Path(..., description="Bank ID")
):
    """Assign a client to a segment"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    success = await bank_service.assign_client_to_segment(
        bank_id, assignment.client_id, assignment.segment_id, auth_context.uid
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to assign client to segment"
        )
    
    return APIResponse(
        success=True,
        data={},
        message="Client assigned to segment successfully"
    )


@router.post("/{bank_id}/client-assignments/bulk-assign", response_model=APIResponse[dict])
@require_permission("manage_client_segments")
async def bulk_assign_clients_to_segments(
    request: Request,
    assignments: BulkClientSegmentAssignment,
    bank_id: str = Path(..., description="Bank ID")
):
    """Bulk assign clients to segments"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    success = await bank_service.bulk_assign_clients_to_segments(
        bank_id, assignments, auth_context.uid
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to bulk assign clients to segments"
        )
    
    return APIResponse(
        success=True,
        data={},
        message=f"Successfully assigned {len(assignments.assignments)} clients to segments"
    )


@router.delete("/{bank_id}/client-assignments/{client_id}/{segment_id}", response_model=APIResponse[dict])
@require_permission("manage_client_segments")
async def remove_client_from_segment(
    request: Request,
    bank_id: str = Path(..., description="Bank ID"),
    client_id: str = Path(..., description="Client ID"),
    segment_id: str = Path(..., description="Segment ID")
):
    """Remove a client from a segment"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    success = await bank_service.remove_client_from_segment(bank_id, client_id, segment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to remove client from segment"
        )
    
    return APIResponse(
        success=True,
        data={},
        message="Client removed from segment successfully"
    )


# ========== Bank System Settings Endpoints ==========

@router.get("/{bank_id}/system-settings", response_model=APIResponse[BankSystemSettings])
@require_permission("manage_bank_settings")
async def get_bank_system_settings(
    request: Request,
    bank_id: str = Path(..., description="Bank ID")
):
    """Get bank system settings"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    settings = await bank_service.get_bank_system_settings(bank_id)
    
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bank system settings"
        )
    
    return APIResponse(
        success=True,
        data=settings,
        message="Bank system settings retrieved successfully"
    )


@router.put("/{bank_id}/system-settings", response_model=APIResponse[BankSystemSettings])
@require_permission("manage_bank_settings")
async def update_bank_system_settings(
    request: Request,
    settings_update: BankSystemSettingsUpdate,
    bank_id: str = Path(..., description="Bank ID")
):
    """Update bank system settings"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    updated_settings = await bank_service.update_bank_system_settings(
        bank_id, settings_update, auth_context.uid
    )
    
    if updated_settings is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update bank system settings"
        )
    
    return APIResponse(
        success=True,
        data=updated_settings,
        message="Bank system settings updated successfully"
    )


