"""
Bank management routes
"""

from fastapi import APIRouter, Request, HTTPException, status, Path, File, UploadFile
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
async def get_client_segments(
    request: Request,
    bank_id: str = Path(..., description="Bank ID")
):
    """Get all client segments for a bank"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not await bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    segments = await bank_service.get_client_segments(bank_id)
    
    return APIResponse(
        success=True,
        data=segments,
        message="Client segments retrieved successfully"
    )


@router.get("/{bank_id}/client-segments/{segment_id}", response_model=APIResponse[ClientSegment])
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
    
    if not await bank_service.bank_exists(bank_id):
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
async def get_settlement_letters(
    request: Request,
    bank_id: str = Path(..., description="Bank ID")
):
    """Get all settlement instruction letters for a bank"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not await bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    letters = await bank_service.get_settlement_letters(bank_id)
    
    return APIResponse(
        success=True,
        data=letters,
        message="Settlement letters retrieved successfully"
    )


@router.get("/{bank_id}/settlement-letters/{letter_id}", response_model=APIResponse[SettlementInstructionLetter])
async def get_settlement_letter(
    request: Request,
    bank_id: str = Path(..., description="Bank ID"),
    letter_id: str = Path(..., description="Letter ID")
):
    """Get specific settlement instruction letter"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    letter = await bank_service.get_settlement_letter(bank_id, letter_id)
    
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
    """Create a new settlement instruction letter"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not await bank_service.bank_exists(bank_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
    
    created_letter = await bank_service.create_settlement_letter(
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
    
    updated_letter = await bank_service.update_settlement_letter(
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
    
    success = await bank_service.delete_settlement_letter(bank_id, letter_id)
    
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
async def get_client_segment_assignments(
    request: Request,
    bank_id: str = Path(..., description="Bank ID")
):
    """Get all client-segment assignments for a bank"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not await bank_service.bank_exists(bank_id):
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
async def get_bank_system_settings(
    request: Request,
    bank_id: str = Path(..., description="Bank ID")
):
    """Get bank system settings"""
    auth_context = get_auth_context(request)
    validate_bank_access(auth_context, bank_id)
    
    bank_service = BankService()
    
    if not await bank_service.bank_exists(bank_id):
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


