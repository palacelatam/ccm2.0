"""
Client management routes
"""

from fastapi import APIRouter, Request, HTTPException, status, Path, UploadFile, File, Form
from typing import List, Dict, Any
from datetime import datetime
import logging

from api.middleware.auth_middleware import get_auth_context, require_permission
from services.client_service import ClientService
from services.bank_service import BankService
from services.email_parser import EmailParserService
from services.matching_service import MatchingService
from models.base import APIResponse
from models.client import (
    ClientSettings, ClientSettingsUpdate,
    BankAccount, BankAccountCreate, BankAccountUpdate,
    SettlementRule, SettlementRuleCreate, SettlementRuleUpdate,
    DataMapping, DataMappingCreate, DataMappingUpdate,
    UnmatchedTrade, EmailConfirmation, TradeMatch, ProcessingResult
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


# ========== Trade Management Endpoints ==========

@router.get("/{client_id}/unmatched-trades", response_model=APIResponse[List[Dict[str, Any]]])
async def get_unmatched_trades(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get all unmatched trades for client"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    trades = await client_service.get_unmatched_trades(client_id)
    
    return APIResponse(
        success=True,
        data=trades,
        message=f"Retrieved {len(trades)} unmatched trades"
    )


@router.get("/{client_id}/email-confirmations", response_model=APIResponse[List[EmailConfirmation]])
async def get_email_confirmations(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get all email confirmations for client"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    emails = await client_service.get_email_confirmations(client_id)
    
    return APIResponse(
        success=True,
        data=emails,
        message=f"Retrieved {len(emails)} email confirmations"
    )


@router.get("/{client_id}/matches", response_model=APIResponse[List[TradeMatch]])
async def get_matches(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get all trade matches for client"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    matches = await client_service.get_matches(client_id)
    
    return APIResponse(
        success=True,
        data=matches,
        message=f"Retrieved {len(matches)} trade matches"
    )


@router.get("/{client_id}/matched-trades", response_model=APIResponse[List[Dict[str, Any]]])
async def get_matched_trades(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get matched trades with enriched match information"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    matched_trades = await client_service.get_matched_trades(client_id)
    
    return APIResponse(
        success=True,
        data=matched_trades,
        message=f"Retrieved {len(matched_trades)} matched trades"
    )


@router.get("/{client_id}/all-email-confirmations", response_model=APIResponse[List[Dict[str, Any]]])
async def get_all_email_confirmations(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get all email confirmations with extracted trade data"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    emails = await client_service.get_all_email_confirmations(client_id)
    
    return APIResponse(
        success=True,
        data=emails,
        message=f"Retrieved {len(emails)} email confirmations"
    )


@router.post("/{client_id}/upload-trades", response_model=APIResponse[Dict[str, Any]])
async def upload_trades(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    file: UploadFile = File(..., description="CSV file with trade data"),
    overwrite: bool = Form(False, description="Whether to overwrite existing unmatched trades")
):
    """Upload CSV file with trade data"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    # Check file type - now only CSV
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be CSV (.csv) format"
        )
    
    client_service = ClientService()
    
    # Check client exists
    if not await client_service.client_exists(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Read file content
        csv_content = await file.read()
        
        # Try to decode with different encodings
        try:
            csv_string = csv_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                csv_string = csv_content.decode('latin-1')
            except UnicodeDecodeError:
                try:
                    csv_string = csv_content.decode('cp1252')
                except UnicodeDecodeError:
                    csv_string = csv_content.decode('utf-8', errors='replace')
        
        # Process CSV and insert trades
        result = await client_service.process_csv_upload(
            client_id=client_id,
            csv_content=csv_string,
            overwrite_existing=overwrite,
            uploaded_by=auth_context.uid,
            filename=file.filename
        )
        
        if not result['success']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV processing failed: {'; '.join(result['errors'])}"
            )
        
        return APIResponse(
            success=True,
            data=result,
            message=f"Successfully processed {result['records_processed']} trades"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading trade file for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process trade file: {str(e)}"
        )


@router.post("/{client_id}/upload-emails", response_model=APIResponse[Dict[str, Any]])
async def upload_emails(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    file: UploadFile = File(..., description="Email file (.msg/.pdf)")
):
    """Upload .msg/.pdf email files"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    # Check file type
    if not file.filename.lower().endswith(('.msg', '.pdf')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be email (.msg) or PDF (.pdf) format"
        )
    
    client_service = ClientService()
    
    # Check client exists
    if not await client_service.client_exists(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Create upload session
        session_id = await client_service.create_upload_session(
            client_id=client_id,
            file_name=file.filename,
            file_type="emails",
            file_size=file.size,
            uploaded_by=auth_context.uid
        )
        
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create upload session"
            )
        
        # Read file content
        file_content = await file.read()
        
        # Process email file using EmailParserService
        email_parser = EmailParserService()
        email_data, parser_errors = email_parser.process_email_file(
            file_content=file_content,
            filename=file.filename
        )
        
        if parser_errors:
            await client_service.update_upload_session(
                client_id=client_id,
                session_id=session_id,
                records_processed=0,
                records_failed=1,
                status="failed"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Email processing failed: {'; '.join(parser_errors)}"
            )
        
        # Process extracted email data, save to database, and perform matching using unified method
        result = await client_service.process_and_match_email(
            client_id=client_id,
            email_data=email_data,
            session_id=session_id,
            uploaded_by=auth_context.uid,
            filename=file.filename
        )
        
        # Extract results from unified processing
        extracted_trades_count = result.get('trades_extracted', 0)
        matches_found = result.get('matches_found', 0)
        counterparty_name = result.get('counterparty_name', 'Unknown')
        matched_trade_numbers = result.get('matched_trade_numbers', [])
        duplicates_found = result.get('duplicates_found', 0)
        
        await client_service.update_upload_session(
            client_id=client_id,
            session_id=session_id,
            records_processed=extracted_trades_count,
            records_failed=0,
            status="completed"
        )
        
        return APIResponse(
            success=True,
            data={
                "upload_session_id": session_id,
                "email_id": result.get('email_id'),
                "file_name": file.filename,
                "file_size": file.size,
                "trades_extracted": extracted_trades_count,
                "matches_found": matches_found,
                "duplicates_found": duplicates_found,
                "confirmation_detected": email_data.get('llm_extracted_data', {}).get('Email', {}).get('Confirmation') == 'Yes',
                "counterparty_name": counterparty_name,
                "matched_trade_numbers": matched_trade_numbers
            },
            message=f"Successfully processed email file with {extracted_trades_count} trades extracted and {matches_found} matches found"
        )
        
    except Exception as e:
        logger.error(f"Error uploading email file for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process email file: {str(e)}"
        )


@router.delete("/{client_id}/unmatched-trades", response_model=APIResponse[Dict[str, Any]])
async def delete_all_unmatched_trades(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Delete all unmatched trades for a client"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    # Check client exists
    if not await client_service.client_exists(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Get current count of unmatched trades before deletion
        trades = await client_service.get_unmatched_trades(client_id)
        trades_count = len(trades)
        
        if trades_count == 0:
            return APIResponse(
                success=True,
                data={
                    "trades_deleted": 0,
                    "message": "No unmatched trades to delete"
                },
                message="No unmatched trades found"
            )
        
        # Delete all unmatched trades
        deleted_count = await client_service.delete_all_unmatched_trades(
            client_id=client_id,
            deleted_by=auth_context.uid
        )
        
        return APIResponse(
            success=True,
            data={
                "trades_deleted": deleted_count,
                "message": f"Successfully deleted {deleted_count} unmatched trades"
            },
            message=f"Deleted {deleted_count} unmatched trades"
        )
        
    except Exception as e:
        logger.error(f"Error deleting unmatched trades for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete unmatched trades: {str(e)}"
        )


@router.get("/{client_id}/email-confirmations", response_model=APIResponse[List[Dict[str, Any]]])
async def get_email_confirmations(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Get all email confirmations for a client"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    # Check client exists
    if not await client_service.client_exists(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        emails = await client_service.get_email_confirmations(client_id)
        
        return APIResponse(
            success=True,
            data=emails,
            message=f"Retrieved {len(emails)} email confirmations"
        )
        
    except Exception as e:
        logger.error(f"Error retrieving email confirmations for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve email confirmations: {str(e)}"
        )


@router.patch("/{client_id}/email-confirmations/{email_id}/status", response_model=APIResponse[Dict[str, Any]])
async def update_email_confirmation_status(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    email_id: str = Path(..., description="Email Confirmation ID"),
    status_update: Dict[str, Any] = None
):
    """Update the status of an email confirmation"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    # Parse request body
    body = await request.json()
    new_status = body.get('status')
    updated_by = body.get('updatedBy', auth_context.uid)
    updated_at = body.get('updatedAt')
    
    if not new_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status field is required"
        )
    
    client_service = ClientService()
    
    # Check client exists
    if not await client_service.client_exists(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Update the email confirmation status
        updated_email = await client_service.update_email_confirmation_status(
            client_id=client_id,
            email_id=email_id,
            status=new_status,
            updated_by=updated_by,
            updated_at=updated_at
        )
        
        if not updated_email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Email confirmation not found"
            )
        
        return APIResponse(
            success=True,
            data=updated_email,
            message=f"Email confirmation status updated to {new_status}"
        )
        
    except Exception as e:
        logger.error(f"Error updating email confirmation status for client {client_id}, email {email_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update email confirmation status: {str(e)}"
        )


@router.post("/{client_id}/process-matches", response_model=APIResponse[Dict[str, Any]])
async def process_matches(
    request: Request,
    client_id: str = Path(..., description="Client ID")
):
    """Run matching algorithm on unmatched trades and emails"""
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    client_service = ClientService()
    
    # Check client exists
    if not await client_service.client_exists(client_id):
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        # Get unmatched trades and email confirmations
        unmatched_trades = await client_service.get_unmatched_trades(client_id)
        email_confirmations = await client_service.get_email_confirmations(client_id)
        
        logger.info(f"Found {len(unmatched_trades)} unmatched trades and {len(email_confirmations)} email confirmations for matching")
        
        # Initialize matching service
        matching_service = MatchingService()
        
        matches_found = 0
        confidence_scores = []
        total_processed = 0
        
        # Process each email confirmation
        for email_confirmation in email_confirmations:
            # Skip if already processed or no LLM data
            if email_confirmation.get('status') != 'unmatched':
                continue
                
            # Extract LLM data from email confirmation
            llm_data = email_confirmation.get('llmExtractedData', {})
            if not llm_data or llm_data.get('Email', {}).get('Confirmation', '').lower() != 'yes':
                continue
            
            # Get trades from LLM extraction
            email_trades = llm_data.get('Trades', [])
            if not email_trades:
                continue
            
            # Extract email metadata
            email_metadata = {
                'senderEmail': email_confirmation.get('senderEmail', ''),
                'subject': email_confirmation.get('subject', ''),
                'emailDate': email_confirmation.get('emailDate', ''),
                'emailTime': email_confirmation.get('emailTime', ''),
                'bodyContent': email_confirmation.get('bodyContent', '')
            }
            
            # Run matching algorithm
            match_results = matching_service.match_email_trades_with_client_trades(
                email_trades, unmatched_trades, email_metadata
            )
            
            # Process match results
            for match_result in match_results:
                total_processed += 1
                
                if match_result['matched_client_trade'] is not None:
                    # Match found - save it
                    match_id = match_result['match_id']
                    confidence = match_result['confidence']
                    status = match_result['status']
                    
                    # Create match record in database
                    await client_service.create_match(
                        client_id=client_id,
                        trade_id=match_result['matched_client_trade'].get('id', ''),
                        email_id=email_confirmation.get('id', ''),
                        confidence_score=confidence / 100,  # Convert percentage to decimal
                        match_reasons=match_result['match_reasons'],
                        # Note: Manual matches don't trigger automated emails (trade_comparison_result=None)
                    )
                    
                    matches_found += 1
                    confidence_scores.append(confidence)
                    
                    logger.info(f"Match created - Trade: {match_result['matched_client_trade'].get('TradeNumber')}, "
                              f"Email: {email_confirmation.get('subject', '')}, "
                              f"Confidence: {confidence}%, Status: {status}, Match ID: {match_id}")
                else:
                    # No match found - this will show as "Unrecognized" in the grid
                    logger.info(f"No match found for email trade: {match_result['email_trade'].get('TradeNumber', 'Unknown')}")
        
        avg_confidence = round(sum(confidence_scores) / len(confidence_scores)) if confidence_scores else 0
        
        return APIResponse(
            success=True,
            data={
                "unmatched_trades": len(unmatched_trades),
                "email_confirmations": len(email_confirmations),
                "trades_processed": total_processed,
                "matches_found": matches_found,
                "average_confidence": avg_confidence,
                "confidence_scores": confidence_scores,
            },
            message=f"Processed {total_processed} trades. Found {matches_found} matches with average confidence of {avg_confidence}%"
        )
        
    except Exception as e:
        logger.error(f"Error processing matches for client {client_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process matches: {str(e)}"
        )


@router.post("/{client_id}/settlement-instructions/generate", response_model=APIResponse[Dict[str, Any]])
async def generate_settlement_instruction(
    request: Request,
    client_id: str = Path(..., description="Client ID"),
    trade_number: str = Form(..., description="Client trade number"),
    bank_trade_number: str = Form(None, description="Bank trade number from email")
):
    """
    Generate a settlement instruction document for a specific trade
    
    This endpoint is called manually from the UI when a user wants to generate
    a settlement instruction document on-demand.
    """
    auth_context = get_auth_context(request)
    validate_client_access(auth_context, client_id)
    
    try:
        # Step 2: Fetch and validate trade data
        logger.info(f"Settlement instruction generation requested for client {client_id}, trade {trade_number}")
        
        client_service = ClientService()
        
        # Verify client exists
        if not await client_service.client_exists(client_id):
            raise HTTPException(status_code=404, detail="Client not found")
        
        # Fetch the trade from Firestore
        trades_ref = client_service.db.collection('clients').document(client_id).collection('trades')
        trades_query = trades_ref.where('TradeNumber', '==', trade_number).limit(1)
        trades = trades_query.get()
        
        if not trades:
            logger.error(f"Trade {trade_number} not found for client {client_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trade {trade_number} not found"
            )
        
        trade_doc = trades[0]
        trade_data = trade_doc.to_dict()
        trade_data['id'] = trade_doc.id
        trade_data['client_id'] = client_id
        
        # Get client name for the trade data
        client_doc = client_service.db.collection('clients').document(client_id).get()
        if client_doc.exists:
            client_info = client_doc.to_dict()
            trade_data['client_name'] = client_info.get('name', client_id)
        
        logger.info(f"Trade found: {trade_data.get('TradeNumber')} - {trade_data.get('CounterpartyName')}")
        logger.info(f"Trade details: Product={trade_data.get('ProductType')}, Direction={trade_data.get('Direction')}, "
                   f"Currencies={trade_data.get('Currency1')}/{trade_data.get('Currency2')}")
        
        # Step 3: Fetch settlement rules and bank accounts, then generate document
        logger.info("Fetching settlement rules and bank accounts...")
        
        # Get settlement rules (reusing logic from test_trade.py)
        settlement_rules_ref = client_service.db.collection('clients').document(client_id).collection('settlementRules')
        settlement_rules_docs = settlement_rules_ref.order_by('priority').stream()
        settlement_rules = [doc.to_dict() for doc in settlement_rules_docs]
        
        # Get bank accounts
        bank_accounts_ref = client_service.db.collection('clients').document(client_id).collection('bankAccounts')
        bank_accounts_docs = bank_accounts_ref.stream()
        bank_accounts = [doc.to_dict() for doc in bank_accounts_docs]
        
        logger.info(f"Found {len(settlement_rules)} settlement rules and {len(bank_accounts)} bank accounts")
        
        # Find matching settlement rules (logic from test_trade.py)
        def find_matching_settlement_rules(trade_data, settlement_rules):
            if not settlement_rules:
                return None
                
            trade_counterparty = trade_data.get('CounterpartyName', '').lower()
            trade_currency1 = trade_data.get('Currency1', '')
            trade_currency2 = trade_data.get('Currency2', '')
            trade_product = trade_data.get('ProductType', '')
            trade_direction = trade_data.get('Direction', '').upper()
            settlement_type = trade_data.get('SettlementType', '')
            settlement_currency = trade_data.get('SettlementCurrency', '')
            
            logger.info(f"Matching settlement rules - Type: {settlement_type}, Currency: {settlement_currency}")
            
            if settlement_type == "Compensación":
                for rule in settlement_rules:
                    rule_counterparty = rule.get('counterparty', '').lower()
                    rule_product = rule.get('product', '')
                    rule_modalidad = rule.get('modalidad', '')
                    rule_settlement_currency = rule.get('settlementCurrency', '')
                    rule_active = rule.get('active', True)
                    
                    if not rule_active:
                        continue
                        
                    counterparty_match = not rule_counterparty or rule_counterparty in trade_counterparty
                    product_match = not rule_product or rule_product.lower() in trade_product.lower()
                    modalidad_match = rule_modalidad == 'compensacion'
                    currency_match = rule_settlement_currency == settlement_currency
                    
                    if counterparty_match and product_match and modalidad_match and currency_match:
                        logger.info(f"Matched rule: {rule.get('name')} for Compensación")
                        return rule
                        
            elif settlement_type == "Entrega Física":
                if trade_direction == 'BUY':
                    pay_currency = trade_currency2
                    receive_currency = trade_currency1
                else:
                    pay_currency = trade_currency1
                    receive_currency = trade_currency2
                
                for rule in settlement_rules:
                    rule_counterparty = rule.get('counterparty', '').lower()
                    rule_product = rule.get('product', '')
                    rule_modalidad = rule.get('modalidad', '')
                    rule_cargar_currency = rule.get('cargarCurrency', '')
                    rule_abonar_currency = rule.get('abonarCurrency', '')
                    rule_active = rule.get('active', True)
                    
                    if not rule_active:
                        continue
                        
                    counterparty_match = not rule_counterparty or rule_counterparty in trade_counterparty
                    product_match = not rule_product or rule_product.lower() in trade_product.lower()
                    modalidad_match = rule_modalidad == 'entregaFisica'
                    cargar_match = rule_cargar_currency == pay_currency
                    abonar_match = rule_abonar_currency == receive_currency
                    
                    if (counterparty_match and product_match and modalidad_match and 
                        cargar_match and abonar_match):
                        logger.info(f"Matched rule: {rule.get('name')} for Entrega Física")
                        return {
                            'matched_rule': rule,
                            'pay_currency': pay_currency,
                            'receive_currency': receive_currency
                        }
            
            return None
        
        # Find matching bank accounts (logic from test_trade.py) 
        def find_matching_bank_accounts(settlement_rules_matched, bank_accounts):
            if not settlement_rules_matched:
                return None
                
            if isinstance(settlement_rules_matched, dict) and 'matched_rule' in settlement_rules_matched:
                # Entrega Física case
                rule = settlement_rules_matched['matched_rule']
                cargar_bank = rule.get('cargarBankName', '')
                cargar_account_number = rule.get('cargarAccountNumber', '')
                abonar_bank = rule.get('abonarBankName', '')
                abonar_account_number = rule.get('abonarAccountNumber', '')
                
                cargar_account = None
                abonar_account = None
                
                for account in bank_accounts:
                    if (account.get('bankName') == cargar_bank and 
                        account.get('accountNumber') == cargar_account_number):
                        cargar_account = account
                    if (account.get('bankName') == abonar_bank and 
                        account.get('accountNumber') == abonar_account_number):
                        abonar_account = account
                
                if cargar_account and abonar_account:
                    return {
                        'cargar': cargar_account,
                        'abonar': abonar_account
                    }
                return None
            else:
                # Compensación case - get bank account details directly from the settlement rule
                rule = settlement_rules_matched
                
                # Get bank account details directly from settlement rule using correct field names
                # For Compensación, use abonar fields as the primary account
                rule_bank_name = rule.get('abonarBankName', '')
                rule_account_number = rule.get('abonarAccountNumber', '')
                rule_swift_code = rule.get('abonarSwiftCode', '')
                rule_settlement_currency = rule.get('settlementCurrency', '')
                rule_account_name = f"{rule_bank_name} - {rule_settlement_currency}"
                
                logger.info(f"Using bank account details directly from settlement rule: {rule_account_name}")
                logger.info(f"Bank: {rule_bank_name}, Account: {rule_account_number}, Currency: {rule_settlement_currency}")
                
                return {
                    'accountName': rule_account_name,
                    'accountNumber': rule_account_number,
                    'bankName': rule_bank_name,
                    'swiftCode': rule_swift_code,
                    'accountCurrency': rule_settlement_currency
                }
        
        # Find matching settlement rules and bank accounts
        settlement_rules_matched = find_matching_settlement_rules(trade_data, settlement_rules)
        if not settlement_rules_matched:
            logger.error(f"No matching settlement rules found for trade {trade_number}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No matching settlement rules found for this trade. Please check settlement rules configuration."
            )
        
        bank_accounts_matched = find_matching_bank_accounts(settlement_rules_matched, bank_accounts)
        if not bank_accounts_matched:
            logger.error(f"No matching bank accounts found for trade {trade_number}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No matching bank accounts found for the settlement rule. Please check bank account configuration."
            )
        
        # Prepare settlement data (reusing logic from test_trade.py)
        settlement_data = None
        if isinstance(bank_accounts_matched, dict) and 'cargar' in bank_accounts_matched:
            # Physical delivery - two accounts
            cargar_account = bank_accounts_matched.get('cargar')
            abonar_account = bank_accounts_matched.get('abonar')
            
            settlement_data = {
                'cargar_account_name': cargar_account.get('accountName', 'N/A'),
                'cargar_account_number': cargar_account.get('accountNumber', 'N/A'),
                'cargar_bank_name': cargar_account.get('bankName', 'N/A'),
                'cargar_swift_code': cargar_account.get('swiftCode', 'N/A'),
                'cargar_currency': cargar_account.get('accountCurrency', 'N/A'),
                'abonar_account_name': abonar_account.get('accountName', 'N/A'),
                'abonar_account_number': abonar_account.get('accountNumber', 'N/A'),
                'abonar_bank_name': abonar_account.get('bankName', 'N/A'),
                'abonar_swift_code': abonar_account.get('swiftCode', 'N/A'),
                'abonar_currency': abonar_account.get('accountCurrency', 'N/A'),
                'cutoff_time': '15:00 Santiago Time',
                'special_instructions': 'Physical delivery settlement - two-way transfer',
                'central_bank_trade_code': settlement_rules_matched.get('matched_rule', {}).get('centralBankTradeCode', 'N/A'),
                # For backward compatibility
                'account_name': abonar_account.get('accountName', 'N/A'),
                'account_number': abonar_account.get('accountNumber', 'N/A'),
                'bank_name': abonar_account.get('bankName', 'N/A'),
                'swift_code': abonar_account.get('swiftCode', 'N/A')
            }
            logger.info("Settlement data prepared for Physical Delivery (two accounts)")
        else:
            # Compensación - single account (populate both basic and abonar/cargar fields)
            settlement_data = {
                # Basic fields
                'account_name': bank_accounts_matched.get('accountName', 'N/A'),
                'account_number': bank_accounts_matched.get('accountNumber', 'N/A'),
                'bank_name': bank_accounts_matched.get('bankName', 'N/A'),
                'swift_code': bank_accounts_matched.get('swiftCode', 'N/A'),
                
                # Abonar fields (from settlement rule)
                'abonar_account_name': bank_accounts_matched.get('accountName', 'N/A'),
                'abonar_account_number': settlement_rules_matched.get('abonarAccountNumber', 'N/A'),
                'abonar_bank_name': settlement_rules_matched.get('abonarBankName', 'N/A'),
                'abonar_swift_code': settlement_rules_matched.get('abonarSwiftCode', 'N/A'),
                'abonar_currency': settlement_rules_matched.get('abonarCurrency', 'N/A'),
                
                # Cargar fields (from settlement rule - same for Compensación)
                'cargar_account_name': bank_accounts_matched.get('accountName', 'N/A'),
                'cargar_account_number': settlement_rules_matched.get('cargarAccountNumber', 'N/A'),
                'cargar_bank_name': settlement_rules_matched.get('cargarBankName', 'N/A'),
                'cargar_swift_code': settlement_rules_matched.get('cargarSwiftCode', 'N/A'),
                'cargar_currency': settlement_rules_matched.get('cargarCurrency', 'N/A'),
                
                # Other fields
                'cutoff_time': '15:00 Santiago Time',
                'special_instructions': settlement_rules_matched.get('specialInstructions', 'Standard settlement instructions apply.'),
                'central_bank_trade_code': settlement_rules_matched.get('centralBankTradeCode', 'N/A')
            }
            logger.info("Settlement data prepared for Compensación with abonar/cargar fields populated")
        
        # Generate settlement instruction document using existing service
        from services.settlement_instruction_service import settlement_instruction_service
        
        # Map counterparty to bank ID (reusing logic from test_trade.py)
        counterparty = trade_data.get('CounterpartyName', '')
        if 'banco abc' in counterparty.lower():
            bank_id = "banco-abc"
        else:
            bank_id = counterparty.lower().replace(' ', '-').replace('ó', 'o')
        
        # Get client segment ID if available
        client_segment_id = trade_data.get('client_segment_id')
        
        # Ensure trade has Product field for template matching
        product = trade_data.get('ProductType', trade_data.get('Product', 'N/A'))
        trade_data_with_product = trade_data.copy()
        trade_data_with_product['Product'] = product
        
        logger.info(f"Generating document with bank_id={bank_id}, segment_id={client_segment_id}")
        
        # Generate the document
        result = await settlement_instruction_service.generate_settlement_instruction(
            trade_data=trade_data_with_product,
            bank_id=bank_id,
            client_segment_id=client_segment_id,
            settlement_data=settlement_data
        )
        
        if not result['success']:
            logger.error(f"Document generation failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate settlement instruction document: {result.get('error')}"
            )
        
        logger.info(f"Document generated successfully: {result['document_path']}")
        
        # For Step 3 testing, return document generation results
        response_data = {
            "trade_number": trade_number,
            "bank_trade_number": bank_trade_number,
            "status": "document_generated",
            "document_path": result['document_path'],
            "template_used": result['template_used'],
            "template_id": result.get('template_id'),
            "variables_populated": result['variables_populated'],
            "settlement_rules_found": len(settlement_rules),
            "bank_accounts_found": len(bank_accounts),
            "settlement_type": trade_data.get('SettlementType'),
            "message": "Settlement instruction document generated successfully (Step 3)",
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        
        return APIResponse(
            success=True,
            data=response_data,
            message="Settlement instruction document generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating settlement instruction for client {client_id}, trade {trade_number}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate settlement instruction: {str(e)}"
        )