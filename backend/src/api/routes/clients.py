"""
Client management routes
"""

from fastapi import APIRouter, Request, HTTPException, status, Path
from typing import List, Dict, Any
import logging

from api.middleware.auth_middleware import get_auth_context, require_permission
from services.client_service import ClientService
from services.bank_service import BankService
from models.base import APIResponse
from models.client import (
    ClientSettings, ClientSettingsUpdate,
    BankAccount, BankAccountCreate, BankAccountUpdate,
    SettlementRule, SettlementRuleCreate, SettlementRuleUpdate,
    DataMapping, DataMappingCreate, DataMappingUpdate
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("", response_model=APIResponse[List[Dict[str, Any]]])
async def get_all_clients(request: Request):
    """Get all clients (independent of banks)"""
    auth_context = get_auth_context(request)
    
    client_service = ClientService()
    clients = client_service.get_all_clients()
    
    return APIResponse(
        success=True,
        data=clients,
        message="Clients retrieved successfully"
    )


def validate_client_access(auth_context, client_id: str):
    """Validate user has access to the specified client"""
    if auth_context.organization_type != "client" or auth_context.organization_id != client_id:
        if not (auth_context.organization_type == "bank" and auth_context.has_permission("view_all_clients")):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this client"
            )


# ========== Client Settings Endpoints ==========

@router.get("/{client_id}/settings", response_model=APIResponse[ClientSettings])
async def get_client_settings(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get client settings configuration"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    # Check if client exists
    if not await client_service.client_exists(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    settings = await client_service.get_client_settings(client_id)
    
    if settings is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client settings"
        )
    
    return APIResponse(
        success=True,
        data=settings,
        message="Client settings retrieved successfully"
    )


@router.put("/{client_id}/settings", response_model=APIResponse[ClientSettings])
@require_permission("manage_settings")
async def update_client_settings(
    request: Request,
    settings_update: ClientSettingsUpdate,
    client_id: str = Path(..., description="Client ID")
):
    """Update client settings configuration"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    # Check if client exists
    if not await client_service.client_exists(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    updated_settings = await client_service.update_client_settings(
        client_id, settings_update, auth_context.uid
    )
    
    if updated_settings is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update client settings"
        )
    
    return APIResponse(
        success=True,
        data=updated_settings,
        message="Client settings updated successfully"
    )


# ========== Bank Account Endpoints ==========

@router.get("/{client_id}/bank-accounts", response_model=APIResponse[List[BankAccount]])
async def get_bank_accounts(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get all bank accounts for a client"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    if not await client_service.client_exists(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    accounts = await client_service.get_bank_accounts(client_id)
    
    return APIResponse(
        success=True,
        data=accounts,
        message="Bank accounts retrieved successfully"
    )


@router.get("/{client_id}/bank-accounts/{account_id}", response_model=APIResponse[BankAccount])
async def get_bank_account(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    account_id: str = Path(..., description="Account ID")
):
    """Get specific bank account"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    account = await client_service.get_bank_account(client_id, account_id)
    
    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found"
        )
    
    return APIResponse(
        success=True,
        data=account,
        message="Bank account retrieved successfully"
    )


@router.post("/{client_id}/bank-accounts", response_model=APIResponse[BankAccount])
@require_permission("manage_bank_accounts")
async def create_bank_account(
    request: Request,
    account_data: BankAccountCreate,
    client_id: str = Path(..., description="Client ID")
):
    """Create a new bank account"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    if not await client_service.client_exists(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    created_account = await client_service.create_bank_account(
        client_id, account_data, auth_context.uid
    )
    
    if created_account is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create bank account"
        )
    
    return APIResponse(
        success=True,
        data=created_account,
        message="Bank account created successfully"
    )


@router.put("/{client_id}/bank-accounts/{account_id}", response_model=APIResponse[BankAccount])
@require_permission("manage_bank_accounts")
async def update_bank_account(
    request: Request,
    account_update: BankAccountUpdate,
    client_id: str = Path(..., description="Client ID"),
    account_id: str = Path(..., description="Account ID")
):
    """Update bank account"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    updated_account = await client_service.update_bank_account(
        client_id, account_id, account_update, auth_context.uid
    )
    
    if updated_account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found or failed to update"
        )
    
    return APIResponse(
        success=True,
        data=updated_account,
        message="Bank account updated successfully"
    )


@router.delete("/{client_id}/bank-accounts/{account_id}", response_model=APIResponse[dict])
@require_permission("manage_bank_accounts")
async def delete_bank_account(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    account_id: str = Path(..., description="Account ID")
):
    """Delete bank account"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    success = await client_service.delete_bank_account(client_id, account_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank account not found or failed to delete"
        )
    
    return APIResponse(
        success=True,
        data={},
        message="Bank account deleted successfully"
    )


# ========== Settlement Rules Endpoints ==========

@router.get("/{client_id}/settlement-rules", response_model=APIResponse[List[SettlementRule]])
async def get_settlement_rules(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get all settlement rules for a client"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    if not await client_service.client_exists(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    rules = await client_service.get_settlement_rules(client_id)
    
    return APIResponse(
        success=True,
        data=rules,
        message="Settlement rules retrieved successfully"
    )


@router.get("/{client_id}/settlement-rules/{rule_id}", response_model=APIResponse[SettlementRule])
async def get_settlement_rule(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    rule_id: str = Path(..., description="Rule ID")
):
    """Get specific settlement rule"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    rule = await client_service.get_settlement_rule(client_id, rule_id)
    
    if rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement rule not found"
        )
    
    return APIResponse(
        success=True,
        data=rule,
        message="Settlement rule retrieved successfully"
    )


@router.post("/{client_id}/settlement-rules", response_model=APIResponse[SettlementRule])
@require_permission("manage_settlement_rules")
async def create_settlement_rule(
    request: Request,
    rule_data: SettlementRuleCreate,
    client_id: str = Path(..., description="Client ID")
):
    """Create a new settlement rule"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    if not await client_service.client_exists(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    created_rule = await client_service.create_settlement_rule(
        client_id, rule_data, auth_context.uid
    )
    
    if created_rule is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create settlement rule"
        )
    
    return APIResponse(
        success=True,
        data=created_rule,
        message="Settlement rule created successfully"
    )


@router.put("/{client_id}/settlement-rules/{rule_id}", response_model=APIResponse[SettlementRule])
@require_permission("manage_settlement_rules")
async def update_settlement_rule(
    request: Request,
    rule_update: SettlementRuleUpdate,
    client_id: str = Path(..., description="Client ID"),
    rule_id: str = Path(..., description="Rule ID")
):
    """Update settlement rule"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    updated_rule = await client_service.update_settlement_rule(
        client_id, rule_id, rule_update, auth_context.uid
    )
    
    if updated_rule is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement rule not found or failed to update"
        )
    
    return APIResponse(
        success=True,
        data=updated_rule,
        message="Settlement rule updated successfully"
    )


@router.delete("/{client_id}/settlement-rules/{rule_id}", response_model=APIResponse[dict])
@require_permission("manage_settlement_rules")
async def delete_settlement_rule(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    rule_id: str = Path(..., description="Rule ID")
):
    """Delete settlement rule"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    success = await client_service.delete_settlement_rule(client_id, rule_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Settlement rule not found or failed to delete"
        )
    
    return APIResponse(
        success=True,
        data={},
        message="Settlement rule deleted successfully"
    )


# ========== Data Mapping Endpoints ==========

@router.get("/{client_id}/data-mappings", response_model=APIResponse[List[DataMapping]])
async def get_data_mappings(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get all data mappings for a client"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    if not await client_service.client_exists(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    mappings = await client_service.get_data_mappings(client_id)
    
    return APIResponse(
        success=True,
        data=mappings,
        message="Data mappings retrieved successfully"
    )


@router.get("/{client_id}/data-mappings/{mapping_id}", response_model=APIResponse[DataMapping])
async def get_data_mapping(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    mapping_id: str = Path(..., description="Mapping ID")
):
    """Get specific data mapping"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    mapping = await client_service.get_data_mapping(client_id, mapping_id)
    
    if mapping is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data mapping not found"
        )
    
    return APIResponse(
        success=True,
        data=mapping,
        message="Data mapping retrieved successfully"
    )


@router.post("/{client_id}/data-mappings", response_model=APIResponse[DataMapping])
@require_permission("manage_data_mappings")
async def create_data_mapping(
    request: Request,
    mapping_data: DataMappingCreate,
    client_id: str = Path(..., description="Client ID")
):
    """Create a new data mapping"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    if not await client_service.client_exists(client_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    created_mapping = await client_service.create_data_mapping(
        client_id, mapping_data, auth_context.uid
    )
    
    if created_mapping is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create data mapping"
        )
    
    return APIResponse(
        success=True,
        data=created_mapping,
        message="Data mapping created successfully"
    )


@router.put("/{client_id}/data-mappings/{mapping_id}", response_model=APIResponse[DataMapping])
@require_permission("manage_data_mappings")
async def update_data_mapping(
    request: Request,
    mapping_update: DataMappingUpdate,
    client_id: str = Path(..., description="Client ID"),
    mapping_id: str = Path(..., description="Mapping ID")
):
    """Update data mapping"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    updated_mapping = await client_service.update_data_mapping(
        client_id, mapping_id, mapping_update, auth_context.uid
    )
    
    if updated_mapping is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data mapping not found or failed to update"
        )
    
    return APIResponse(
        success=True,
        data=updated_mapping,
        message="Data mapping updated successfully"
    )


@router.delete("/{client_id}/data-mappings/{mapping_id}", response_model=APIResponse[dict])
@require_permission("manage_data_mappings")
async def delete_data_mapping(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    mapping_id: str = Path(..., description="Mapping ID")
):
    """Delete data mapping"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    success = await client_service.delete_data_mapping(client_id, mapping_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data mapping not found or failed to delete"
        )
    
    return APIResponse(
        success=True,
        data={},
        message="Data mapping deleted successfully"
    )