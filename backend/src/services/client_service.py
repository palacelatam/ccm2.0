"""
Client service for managing client settings and related data
"""

from typing import Optional, List, Dict, Any, Tuple
from google.cloud.firestore import DocumentReference, Query
import logging
import re
import uuid
from datetime import datetime, timezone

from config.firebase_config import get_cmek_firestore_client
from services.csv_parser import CSVParserService
from services.email_parser import EmailParserService
from services.task_queue_service import task_queue_service
from services.auto_email_service import auto_email_service
from services.auto_sms_service import auto_sms_service
from models.client import (
    ClientSettings, ClientSettingsUpdate,
    BankAccount, BankAccountCreate, BankAccountUpdate,
    SettlementRule, SettlementRuleCreate, SettlementRuleUpdate,
    DataMapping, DataMappingCreate, DataMappingUpdate,
    ClientUserOverride,
    UnmatchedTrade, UnmatchedTradeCreate,
    EmailConfirmation, EmailConfirmationCreate,
    TradeMatch, UploadSession, ProcessingResult
)

logger = logging.getLogger(__name__)


class ClientService:
    """Service for client settings and data management"""
    
    def __init__(self):
        self.db = get_cmek_firestore_client()
        self.csv_parser = CSVParserService()
    
    # ========== Client Management Methods ==========
    
    def get_all_clients(self) -> List[Dict[str, Any]]:
        """Get all clients (independent of banks)"""
        try:
            clients_docs = self.db.collection('clients').stream()
            
            clients = []
            for doc in clients_docs:
                client_data = doc.to_dict()
                client_data['id'] = doc.id
                
                # Handle DocumentReference objects - convert them to strings or resolve them
                if 'bankId' in client_data:
                    if hasattr(client_data['bankId'], 'path'):
                        # It's a DocumentReference, get the ID from the path
                        client_data['bankId'] = client_data['bankId'].path.split('/')[-1]
                
                if 'lastUpdatedBy' in client_data:
                    if hasattr(client_data['lastUpdatedBy'], 'path'):
                        # It's a DocumentReference, get the ID from the path
                        client_data['lastUpdatedBy'] = client_data['lastUpdatedBy'].path.split('/')[-1]
                
                clients.append(client_data)
            
            logger.info(f"Found {len(clients)} clients")
            return clients
            
        except Exception as e:
            logger.error(f"Error getting all clients: {e}")
            return []
    
    async def client_exists(self, client_id: str) -> bool:
        """Check if client exists"""
        try:
            client_doc = self.db.collection('clients').document(client_id).get()
            return client_doc.exists
        except Exception as e:
            logger.error(f"Error checking if client {client_id} exists: {e}")
            return False
    
    def get_client_name(self, client_id: str) -> Optional[str]:
        """Get the client's name from the database"""
        try:
            client_doc = self.db.collection('clients').document(client_id).get()
            if client_doc.exists:
                client_data = client_doc.to_dict()
                return client_data.get('name', client_data.get('organizationName', None))
            return None
        except Exception as e:
            logger.error(f"Error getting client name for {client_id}: {e}")
            return None
    
    # ========== Client Settings Methods ==========
    
    async def get_client_settings(self, client_id: str) -> Optional[ClientSettings]:
        """Get client settings configuration"""
        try:
            settings_doc = self.db.collection('clients').document(client_id).collection('settings').document('configuration').get()
            
            if not settings_doc.exists:
                logger.info(f"No settings found for client {client_id}, returning defaults")
                return ClientSettings()
            
            settings_data = settings_doc.to_dict()
            return ClientSettings(**settings_data)
            
        except Exception as e:
            logger.error(f"Error getting client settings for {client_id}: {e}")
            return None
    
    async def update_client_settings(self, client_id: str, settings_update: ClientSettingsUpdate, updated_by_uid: str) -> Optional[ClientSettings]:
        """Update client settings configuration"""
        try:
            settings_ref = self.db.collection('clients').document(client_id).collection('settings').document('configuration')
            
            # Get current settings or create defaults
            current_settings_doc = settings_ref.get()
            if current_settings_doc.exists:
                current_settings = ClientSettings(**current_settings_doc.to_dict())
            else:
                current_settings = ClientSettings()
            
            # Update only provided fields
            update_data = {}
            
            if settings_update.automation is not None:
                update_data['automation'] = settings_update.automation.dict(by_alias=True)
            
            if settings_update.alerts is not None:
                update_data['alerts'] = settings_update.alerts.dict(by_alias=True)
            
            if settings_update.preferences is not None:
                update_data['preferences'] = settings_update.preferences.dict(by_alias=True)
            
            # Add metadata
            update_data['lastUpdatedAt'] = datetime.now()
            update_data['lastUpdatedBy'] = self.db.collection('users').document(updated_by_uid)
            
            # Update document
            settings_ref.set(update_data, merge=True)
            
            # Return updated settings
            return await self.get_client_settings(client_id)
            
        except Exception as e:
            logger.error(f"Error updating client settings for {client_id}: {e}")
            return None
    
    # ========== Bank Account Methods ==========
    
    async def get_bank_accounts(self, client_id: str) -> List[BankAccount]:
        """Get all bank accounts for a client"""
        try:
            accounts_collection = self.db.collection('clients').document(client_id).collection('bankAccounts')
            docs = accounts_collection.stream()
            
            accounts = []
            for doc in docs:
                account_data = doc.to_dict()
                account_data['id'] = doc.id
                accounts.append(BankAccount(**account_data))
            
            return accounts
            
        except Exception as e:
            logger.error(f"Error getting bank accounts for client {client_id}: {e}")
            return []
    
    async def get_bank_account(self, client_id: str, account_id: str) -> Optional[BankAccount]:
        """Get specific bank account"""
        try:
            account_doc = self.db.collection('clients').document(client_id).collection('bankAccounts').document(account_id).get()
            
            if not account_doc.exists:
                return None
            
            account_data = account_doc.to_dict()
            account_data['id'] = account_doc.id
            return BankAccount(**account_data)
            
        except Exception as e:
            logger.error(f"Error getting bank account {account_id} for client {client_id}: {e}")
            return None
    
    async def create_bank_account(self, client_id: str, account_data: BankAccountCreate, created_by_uid: str) -> Optional[BankAccount]:
        """Create a new bank account"""
        try:
            accounts_collection = self.db.collection('clients').document(client_id).collection('bankAccounts')
            
            # Convert to dict with metadata
            account_dict = account_data.dict(by_alias=True)
            account_dict.update({
                'active': True,
                'createdAt': datetime.now(),
                'lastUpdatedAt': datetime.now(),
                'lastUpdatedBy': self.db.collection('users').document(created_by_uid)
            })
            
            # If this is set as default, unset other defaults for same currency
            if account_data.is_default:
                await self._unset_default_accounts(client_id, account_data.account_currency)
            
            # Create document
            doc_ref = accounts_collection.add(account_dict)[1]
            
            # Return created account
            return await self.get_bank_account(client_id, doc_ref.id)
            
        except Exception as e:
            logger.error(f"Error creating bank account for client {client_id}: {e}")
            return None
    
    async def update_bank_account(self, client_id: str, account_id: str, account_update: BankAccountUpdate, updated_by_uid: str) -> Optional[BankAccount]:
        """Update bank account"""
        try:
            account_ref = self.db.collection('clients').document(client_id).collection('bankAccounts').document(account_id)
            
            # Build update data
            update_data = {}
            for field, value in account_update.dict(by_alias=True, exclude_none=True).items():
                update_data[field] = value
            
            # Add metadata
            update_data['lastUpdatedAt'] = datetime.now()
            update_data['lastUpdatedBy'] = self.db.collection('users').document(updated_by_uid)
            
            # If setting as default, unset other defaults for same currency
            if account_update.is_default:
                current_account = await self.get_bank_account(client_id, account_id)
                if current_account:
                    await self._unset_default_accounts(client_id, current_account.account_currency, exclude_account_id=account_id)
            
            # Update document
            account_ref.update(update_data)
            
            # Return updated account
            return await self.get_bank_account(client_id, account_id)
            
        except Exception as e:
            logger.error(f"Error updating bank account {account_id} for client {client_id}: {e}")
            return None
    
    async def delete_bank_account(self, client_id: str, account_id: str) -> bool:
        """Delete bank account"""
        try:
            account_ref = self.db.collection('clients').document(client_id).collection('bankAccounts').document(account_id)
            account_ref.delete()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting bank account {account_id} for client {client_id}: {e}")
            return False
    
    async def _unset_default_accounts(self, client_id: str, currency: str, exclude_account_id: str = None):
        """Helper method to unset default flag for accounts of same currency"""
        try:
            accounts_collection = self.db.collection('clients').document(client_id).collection('bankAccounts')
            query = accounts_collection.where('accountCurrency', '==', currency).where('isDefault', '==', True)
            
            docs = query.stream()
            for doc in docs:
                if exclude_account_id and doc.id == exclude_account_id:
                    continue
                doc.reference.update({'isDefault': False})
                
        except Exception as e:
            logger.error(f"Error unsetting default accounts for client {client_id}, currency {currency}: {e}")
    
    # ========== Settlement Rules Methods ==========
    
    async def get_settlement_rules(self, client_id: str) -> List[SettlementRule]:
        """Get all settlement rules for a client"""
        try:
            rules_collection = self.db.collection('clients').document(client_id).collection('settlementRules')
            docs = rules_collection.order_by('priority').stream()
            
            rules = []
            for doc in docs:
                rule_data = doc.to_dict()
                document_id = doc.id
                
                # Debug logging - log both the document and its data
                logger.info(f"Raw Firestore document: id='{document_id}', exists={doc.exists}")
                logger.info(f"Document data: {rule_data}")
                
                # Ensure ID is set, generate one if missing
                if document_id and document_id.strip():
                    rule_data['id'] = document_id
                    logger.info(f"Using document ID: {document_id}")
                else:
                    # Generate a consistent ID based on rule data
                    generated_id = f"rule-{rule_data.get('priority', 1)}-{rule_data.get('name', 'unknown').replace(' ', '-').lower()}"
                    rule_data['id'] = generated_id
                    logger.warning(f"Generated ID for rule: {generated_id}")
                
                # Also log the final rule data that will be returned
                logger.info(f"Final rule data: id={rule_data.get('id')}, name={rule_data.get('name')}, priority={rule_data.get('priority')}")
                
                rules.append(SettlementRule(**rule_data))
            
            logger.info(f"Returning {len(rules)} settlement rules for client {client_id}")
            return rules
            
        except Exception as e:
            logger.error(f"Error getting settlement rules for client {client_id}: {e}")
            return []
    
    async def get_settlement_rule(self, client_id: str, rule_id: str) -> Optional[SettlementRule]:
        """Get specific settlement rule"""
        try:
            rule_doc = self.db.collection('clients').document(client_id).collection('settlementRules').document(rule_id).get()
            
            if not rule_doc.exists:
                return None
            
            rule_data = rule_doc.to_dict()
            rule_data['id'] = rule_doc.id
            return SettlementRule(**rule_data)
            
        except Exception as e:
            logger.error(f"Error getting settlement rule {rule_id} for client {client_id}: {e}")
            return None
    
    async def create_settlement_rule(self, client_id: str, rule_data: SettlementRuleCreate, created_by_uid: str) -> Optional[SettlementRule]:
        """Create a new settlement rule"""
        try:
            rules_collection = self.db.collection('clients').document(client_id).collection('settlementRules')
            
            # Convert to dict with metadata
            rule_dict = rule_data.dict(by_alias=True)
            rule_dict.update({
                'createdAt': datetime.now(),
                'lastUpdatedAt': datetime.now(),
                'lastUpdatedBy': self.db.collection('users').document(created_by_uid)
            })
            
            # If active status is not provided, default to True
            if 'active' not in rule_dict:
                rule_dict['active'] = True
            
            # Create document
            doc_ref = rules_collection.add(rule_dict)[1]
            
            # Return created rule
            return await self.get_settlement_rule(client_id, doc_ref.id)
            
        except Exception as e:
            logger.error(f"Error creating settlement rule for client {client_id}: {e}")
            return None
    
    async def update_settlement_rule(self, client_id: str, rule_id: str, rule_update: SettlementRuleUpdate, updated_by_uid: str) -> Optional[SettlementRule]:
        """Update settlement rule"""
        try:
            print(f"[DEBUG BACKEND] Updating rule {rule_id} for client {client_id}")
            print(f"[DEBUG BACKEND] Rule update data: {rule_update}")
            print(f"[DEBUG BACKEND] Rule update dict: {rule_update.dict()}")
            if hasattr(rule_update, 'settlementCurrency'):
                print(f"[DEBUG BACKEND] settlementCurrency in update: {rule_update.settlementCurrency}")
            if hasattr(rule_update, 'modalidad'):
                print(f"[DEBUG BACKEND] modalidad in update: {rule_update.modalidad}")
            # First, try to find the document by the provided ID
            rule_ref = self.db.collection('clients').document(client_id).collection('settlementRules').document(rule_id)
            
            # Check if document exists with this ID
            if not rule_ref.get().exists:
                logger.warning(f"Settlement rule {rule_id} not found by direct ID, trying to find by generated ID pattern")
                
                # If it's a generated ID (rule-X-name), try to find by matching properties
                if rule_id.startswith('rule-') and '-' in rule_id:
                    # Extract priority from generated ID (rule-1-usd/clp-spot-settlements)
                    parts = rule_id.split('-', 2)  # Split into max 3 parts
                    if len(parts) >= 2 and parts[1].isdigit():
                        expected_priority = int(parts[1])
                        
                        # Find rule by priority (assuming priorities are unique)
                        rules_collection = self.db.collection('clients').document(client_id).collection('settlementRules')
                        docs = rules_collection.where('priority', '==', expected_priority).limit(1).stream()
                        
                        doc_found = None
                        for doc in docs:
                            doc_found = doc
                            break
                        
                        if doc_found:
                            logger.info(f"Found rule by priority {expected_priority}, using document ID {doc_found.id}")
                            rule_ref = doc_found.reference
                        else:
                            logger.error(f"Could not find settlement rule with priority {expected_priority}")
                            return None
                    else:
                        logger.error(f"Could not parse generated ID: {rule_id}")
                        return None
                else:
                    logger.error(f"Settlement rule {rule_id} not found")
                    return None
            
            # Build update data
            update_data = {}
            # Use exclude_none=False to include None values, then handle them appropriately
            rule_dict = rule_update.dict(by_alias=True, exclude_none=False)
            print(f"[DEBUG BACKEND] Rule dict for processing: {rule_dict}")
            
            # Check if this is a priority-only update (from bulk Save Configuration)
            # If only priority has a non-None value, this is a bulk update
            non_none_fields = [field for field, value in rule_dict.items() if value is not None]
            is_priority_only_update = non_none_fields == ['priority']
            print(f"[DEBUG BACKEND] Non-None fields: {non_none_fields}, Priority-only update: {is_priority_only_update}")
            
            for field, value in rule_dict.items():
                print(f"[DEBUG BACKEND] Processing field '{field}' with value: {repr(value)}")
                if value is not None:
                    update_data[field] = value
                    print(f"[DEBUG BACKEND] Added field '{field}' to update_data")
                elif field == 'settlementCurrency' and not is_priority_only_update:
                    # Only delete settlementCurrency if this is a full rule update (not priority-only)
                    # This preserves the field during bulk Save Configuration updates
                    print(f"[DEBUG BACKEND] WARNING: About to DELETE settlementCurrency field (full rule update)!")
                    from google.cloud.firestore import DELETE_FIELD
                    update_data[field] = DELETE_FIELD
                else:
                    if field == 'settlementCurrency' and is_priority_only_update:
                        print(f"[DEBUG BACKEND] Preserving settlementCurrency during priority-only update")
                    else:
                        print(f"[DEBUG BACKEND] Skipping None field '{field}'")
            
            # Add metadata
            update_data['lastUpdatedAt'] = datetime.now()
            update_data['lastUpdatedBy'] = self.db.collection('users').document(updated_by_uid)
            
            print(f"[DEBUG BACKEND] Final update_data: {update_data}")
            logger.info(f"Updating settlement rule {rule_ref.id} with data: {update_data}")
            
            # Update document
            rule_ref.update(update_data)
            
            # Return updated rule using the actual document ID from the reference
            return await self.get_settlement_rule(client_id, rule_ref.id)
            
        except Exception as e:
            logger.error(f"Error updating settlement rule {rule_id} for client {client_id}: {e}")
            return None
    
    async def delete_settlement_rule(self, client_id: str, rule_id: str) -> bool:
        """Delete settlement rule"""
        try:
            rule_ref = self.db.collection('clients').document(client_id).collection('settlementRules').document(rule_id)
            rule_ref.delete()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting settlement rule {rule_id} for client {client_id}: {e}")
            return False
    
    # ========== Data Mapping Methods ==========
    
    async def get_data_mappings(self, client_id: str) -> List[DataMapping]:
        """Get all data mappings for a client"""
        try:
            mappings_collection = self.db.collection('clients').document(client_id).collection('dataMappings')
            docs = mappings_collection.stream()
            
            mappings = []
            for doc in docs:
                mapping_data = doc.to_dict()
                mapping_data['id'] = doc.id
                mappings.append(DataMapping(**mapping_data))
            
            return mappings
            
        except Exception as e:
            logger.error(f"Error getting data mappings for client {client_id}: {e}")
            return []
    
    async def get_data_mapping(self, client_id: str, mapping_id: str) -> Optional[DataMapping]:
        """Get specific data mapping"""
        try:
            mapping_doc = self.db.collection('clients').document(client_id).collection('dataMappings').document(mapping_id).get()
            
            if not mapping_doc.exists:
                return None
            
            mapping_data = mapping_doc.to_dict()
            mapping_data['id'] = mapping_doc.id
            return DataMapping(**mapping_data)
            
        except Exception as e:
            logger.error(f"Error getting data mapping {mapping_id} for client {client_id}: {e}")
            return None
    
    async def create_data_mapping(self, client_id: str, mapping_data: DataMappingCreate, created_by_uid: str) -> Optional[DataMapping]:
        """Create a new data mapping"""
        try:
            mappings_collection = self.db.collection('clients').document(client_id).collection('dataMappings')
            
            # Convert to dict with metadata
            mapping_dict = mapping_data.dict(by_alias=True)
            mapping_dict.update({
                'usageCount': 0,
                'createdAt': datetime.now(),
                'lastUpdatedAt': datetime.now(),
                'lastUpdatedBy': self.db.collection('users').document(created_by_uid)
            })
            
            # If this is set as default, unset other defaults for same file type
            if mapping_data.is_default:
                await self._unset_default_mappings(client_id, mapping_data.file_type)
            
            # Create document
            doc_ref = mappings_collection.add(mapping_dict)[1]
            
            # Return created mapping
            return await self.get_data_mapping(client_id, doc_ref.id)
            
        except Exception as e:
            logger.error(f"Error creating data mapping for client {client_id}: {e}")
            return None
    
    async def update_data_mapping(self, client_id: str, mapping_id: str, mapping_update: DataMappingUpdate, updated_by_uid: str) -> Optional[DataMapping]:
        """Update data mapping"""
        try:
            mapping_ref = self.db.collection('clients').document(client_id).collection('dataMappings').document(mapping_id)
            
            # Build update data
            update_data = {}
            for field, value in mapping_update.dict(by_alias=True, exclude_none=True).items():
                update_data[field] = value
            
            # Add metadata
            update_data['lastUpdatedAt'] = datetime.now()
            update_data['lastUpdatedBy'] = self.db.collection('users').document(updated_by_uid)
            
            # If setting as default, unset other defaults for same file type
            if mapping_update.is_default:
                current_mapping = await self.get_data_mapping(client_id, mapping_id)
                if current_mapping:
                    await self._unset_default_mappings(client_id, current_mapping.file_type, exclude_mapping_id=mapping_id)
            
            # Update document
            mapping_ref.update(update_data)
            
            # Return updated mapping
            return await self.get_data_mapping(client_id, mapping_id)
            
        except Exception as e:
            logger.error(f"Error updating data mapping {mapping_id} for client {client_id}: {e}")
            return None
    
    async def delete_data_mapping(self, client_id: str, mapping_id: str) -> bool:
        """Delete data mapping"""
        try:
            mapping_ref = self.db.collection('clients').document(client_id).collection('dataMappings').document(mapping_id)
            mapping_ref.delete()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting data mapping {mapping_id} for client {client_id}: {e}")
            return False
    
    async def _unset_default_mappings(self, client_id: str, file_type: str, exclude_mapping_id: str = None):
        """Helper method to unset default flag for mappings of same file type"""
        try:
            mappings_collection = self.db.collection('clients').document(client_id).collection('dataMappings')
            query = mappings_collection.where('fileType', '==', file_type).where('isDefault', '==', True)
            
            docs = query.stream()
            for doc in docs:
                if exclude_mapping_id and doc.id == exclude_mapping_id:
                    continue
                doc.reference.update({'isDefault': False})
                
        except Exception as e:
            logger.error(f"Error unsetting default mappings for client {client_id}, file type {file_type}: {e}")
    
    # ========== Trade Management Methods ==========
    
    async def get_unmatched_trades(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all trades for a client (both matched and unmatched)"""
        try:
            trades_ref = self.db.collection('clients').document(client_id).collection('trades')
            docs = trades_ref.stream()  # Get ALL trades, not just unmatched
            
            trades = []
            for doc in docs:
                trade_data = doc.to_dict()
                trade_data['id'] = doc.id
                trades.append(trade_data)  # Return raw dict to preserve v1.0 field names
            
            logger.info(f"Retrieved {len(trades)} total trades for client {client_id}")
            return trades
        except Exception as e:
            logger.error(f"Error getting trades for client {client_id}: {e}")
            return []
    
    async def save_trade_from_upload(self, client_id: str, trade_data: dict, upload_session_id: str) -> bool:
        """Save trade from Excel/CSV upload"""
        try:
            trades_ref = self.db.collection('clients').document(client_id).collection('trades')
            
            trade_doc = {
                **trade_data,
                'status': 'unmatched',
                'uploadSessionId': upload_session_id,
                'createdAt': datetime.now(),
                'organizationId': client_id  # For security rules
            }
            
            trades_ref.add(trade_doc)
            logger.info(f"Saved trade {trade_data.get('tradeNumber')} for client {client_id}")
            return True
        except Exception as e:
            logger.error(f"Error saving trade for client {client_id}: {e}")
            return False
    
    async def get_email_confirmations(self, client_id: str) -> List[EmailConfirmation]:
        """Get all email confirmations for a client"""
        try:
            emails_ref = self.db.collection('clients').document(client_id).collection('emails')
            docs = emails_ref.stream()  # Let frontend handle sorting
            
            emails = []
            for doc in docs:
                email_data = doc.to_dict()
                email_data['id'] = doc.id
                emails.append(EmailConfirmation(**email_data))
            
            logger.info(f"Retrieved {len(emails)} email confirmations for client {client_id}")
            return emails
        except Exception as e:
            logger.error(f"Error getting email confirmations for client {client_id}: {e}")
            return []
    
    async def save_email_confirmation(self, client_id: str, email_data: dict, llm_extracted_data: dict) -> str:
        """Save email confirmation with LLM extracted data"""
        try:
            emails_ref = self.db.collection('clients').document(client_id).collection('emails')
            
            email_doc = {
                **email_data,
                'llmExtractedData': llm_extracted_data,
                'status': 'unmatched',  # Start as unmatched
                'createdAt': datetime.now(),
                'organizationId': client_id
            }
            
            doc_ref = emails_ref.add(email_doc)[1]
            logger.info(f"Saved email confirmation {email_data.get('emailSubject')} for client {client_id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error saving email confirmation for client {client_id}: {e}")
            return None
    
    async def update_email_confirmation_status(
        self, 
        client_id: str, 
        email_id: str, 
        status: str, 
        updated_by: str = None,
        updated_at: str = None
    ) -> Optional[Dict[str, Any]]:
        """Update the status of a specific trade within an email confirmation"""
        try:
            # Handle trade record IDs (e.g., "email_id_trade_0")
            # Extract the actual email ID and trade index
            actual_email_id = email_id
            trade_index = None
            
            if '_trade_' in email_id:
                parts = email_id.split('_trade_')
                actual_email_id = parts[0]
                trade_index = int(parts[1]) if len(parts) > 1 else 0
                logger.info(f"Extracted email ID {actual_email_id} and trade index {trade_index} from {email_id}")
            
            # Get the email confirmation document
            email_ref = self.db.collection('clients').document(client_id).collection('emails').document(actual_email_id)
            email_doc = email_ref.get()
            
            if not email_doc.exists:
                logger.warning(f"Email confirmation {actual_email_id} not found for client {client_id}")
                return None
            
            email_data = email_doc.to_dict()
            
            # Update the status in the specific trade within llmExtractedData.Trades array
            if trade_index is not None:
                llm_data = email_data.get('llmExtractedData', {})
                trades = llm_data.get('Trades', [])
                
                if 0 <= trade_index < len(trades):
                    # Update the status for the specific trade
                    trades[trade_index]['status'] = status
                    trades[trade_index]['lastUpdatedAt'] = updated_at if updated_at else datetime.now().isoformat()
                    trades[trade_index]['lastUpdatedBy'] = updated_by if updated_by else 'system'
                    
                    # Update the document with the modified trades array
                    email_ref.update({
                        'llmExtractedData.Trades': trades,
                        'lastUpdatedAt': updated_at if updated_at else datetime.now().isoformat(),
                        'lastUpdatedBy': updated_by if updated_by else 'system'
                    })
                    
                    logger.info(f"Updated trade {trade_index} status to {status} in email {actual_email_id} for client {client_id}")
                else:
                    logger.warning(f"Trade index {trade_index} out of range for email {actual_email_id}")
                    return None
            else:
                # If no trade index, update the email-level status (fallback for emails without trades)
                email_ref.update({
                    'status': status,
                    'lastUpdatedAt': updated_at if updated_at else datetime.now().isoformat(),
                    'lastUpdatedBy': updated_by if updated_by else 'system'
                })
                logger.info(f"Updated email-level status to {status} for email {actual_email_id}")
            
            # Return the updated data
            updated_doc = email_ref.get()
            email_data = updated_doc.to_dict()
            # Use the original email_id (which might include _trade_X suffix) for consistency with frontend
            email_data['id'] = email_id
            
            return email_data
            
        except Exception as e:
            logger.error(f"Error updating email confirmation status for client {client_id}, email {email_id}: {e}")
            raise
    
    async def get_matches(self, client_id: str) -> List[TradeMatch]:
        """Get all trade matches for a client"""
        try:
            matches_ref = self.db.collection('clients').document(client_id).collection('matches')
            docs = matches_ref.stream()  # Let frontend handle sorting
            
            matches = []
            for doc in docs:
                match_data = doc.to_dict()
                match_data['id'] = doc.id
                matches.append(TradeMatch(**match_data))
            
            logger.info(f"Retrieved {len(matches)} matches for client {client_id}")
            return matches
        except Exception as e:
            logger.error(f"Error getting matches for client {client_id}: {e}")
            return []
    
    async def get_matched_trades(self, client_id: str) -> List[Dict[str, Any]]:
        """Get matched trades with enriched match information"""
        try:
            # Get trades with status = 'matched'
            trades_ref = self.db.collection('clients').document(client_id).collection('trades')
            query = trades_ref.where('status', '==', 'matched')
            trade_docs = query.stream()
            
            enriched_trades = []
            for trade_doc in trade_docs:
                trade_data = trade_doc.to_dict()
                trade_data['id'] = trade_doc.id
                
                # Find the match for this trade
                matches_ref = self.db.collection('clients').document(client_id).collection('matches')
                match_query = matches_ref.where('tradeId', '==', trade_doc.id).limit(1).stream()
                match_docs = list(match_query)
                
                if match_docs:
                    match_data = match_docs[0].to_dict()
                    # Add v1.0 style match fields
                    trade_data['match_id'] = match_data.get('matchId', match_data.get('match_id', match_docs[0].id))  # Check new field first, then fallback
                    #trade_data['match_confidence'] = f"{int(match_data.get('confidenceScore', 0) * 100)}%"
                    trade_data['match_confidence'] = f"{int(match_data.get('confidenceScore', 0))}%"
                    trade_data['match_reasons'] = match_data.get('matchReasons', [])
                    trade_data['identified_at'] = match_data.get('identified_at', match_data.get('createdAt'))
                    
                    # Get differing fields by comparing with the matched email trade
                    email_id = match_data.get('emailId')
                    if email_id:
                        try:
                            # Get the email document
                            email_ref = self.db.collection('clients').document(client_id).collection('emails').document(email_id)
                            email_doc = email_ref.get()
                            if email_doc.exists:
                                email_data = email_doc.to_dict()
                                llm_data = email_data.get('llmExtractedData', {}) or email_data.get('llm_extracted_data', {})
                                email_trades = llm_data.get('Trades', [])
                                
                                # For simplicity, compare with the first email trade (could be improved with better matching)
                                if email_trades:
                                    email_trade = email_trades[0]  # Assuming first trade corresponds to this match
                                    _, differing_fields = self._compare_trade_fields(email_trade, trade_data)
                                    trade_data['differingFields'] = differing_fields
                                else:
                                    trade_data['differingFields'] = []
                            else:
                                trade_data['differingFields'] = []
                        except Exception as e:
                            logger.warning(f"Error fetching differing fields for matched trade {trade_doc.id}: {e}")
                            trade_data['differingFields'] = []
                    else:
                        trade_data['differingFields'] = []
                
                enriched_trades.append(trade_data)
            
            logger.info(f"Retrieved {len(enriched_trades)} matched trades for client {client_id}")
            return enriched_trades
        except Exception as e:
            logger.error(f"Error getting matched trades for client {client_id}: {e}")
            return []
    
    async def get_all_email_confirmations(self, client_id: str) -> List[Dict[str, Any]]:
        """Get all email confirmations with extracted trade data, flattened for frontend display"""
        try:
            emails_ref = self.db.collection('clients').document(client_id).collection('emails')
            # Only get emails where confirmationDetected is true
            docs = emails_ref.where('confirmationDetected', '==', True).stream()
            
            flattened_records = []
            for doc in docs:
                email_data = doc.to_dict()
                email_id = doc.id
                
                # Check if this email has matches
                matches_ref = self.db.collection('clients').document(client_id).collection('matches')
                match_query = matches_ref.where('emailId', '==', email_id).stream()
                match_docs = list(match_query)
                
                # Create match lookup for this email - get actual client trade data
                email_matches = {}
                for match_doc in match_docs:
                    match_data = match_doc.to_dict()
                    trade_id = match_data.get('tradeId')
                    if trade_id:
                        # Get the actual client trade data
                        try:
                            trade_ref = self.db.collection('clients').document(client_id).collection('trades').document(trade_id)
                            trade_doc = trade_ref.get()
                            if trade_doc.exists:
                                client_trade_data = trade_doc.to_dict()
                                # Use TradeNumber as the key for easier lookup
                                trade_number = client_trade_data.get('TradeNumber', '')
                                if trade_number:
                                    email_matches[trade_number] = {
                                        'matchId': match_data.get('matchId', match_data.get('match_id', match_doc.id)),  # Use stored matchId first, then fallback
                                        'matchStatus': 'matched',
                                        'confidenceScore': match_data.get('confidenceScore', 0),
                                        'matchReasons': match_data.get('matchReasons', []),
                                        'clientTradeData': client_trade_data
                                    }
                        except Exception as e:
                            logger.warning(f"Could not fetch client trade {trade_id} for match comparison: {e}")
                
                # Extract LLM data if present (check both possible field names)
                llm_data = email_data.get('llmExtractedData', {}) or email_data.get('llm_extracted_data', {})
                email_info = llm_data.get('Email', {})
                trades = llm_data.get('Trades', [])
                
                # Base email fields from both email document and LLM extracted data
                base_email_fields = {
                    'id': email_id,
                    'emailId': email_id,
                    'createdAt': email_data.get('createdAt'),
                    'filename': email_data.get('filename', ''),
                    
                    # Email metadata - use actual metadata from root level, not LLM extracted
                    'EmailSender': email_data.get('senderEmail', ''),  # Use root level metadata
                    'EmailDate': email_data.get('emailDate', ''),  # Use root level metadata (correct field name)
                    'EmailTime': email_data.get('emailTime', ''),  # Use root level metadata (correct field name)
                    'EmailSubject': email_data.get('subject', ''),  # Use root level metadata
                    'EmailBody': email_data.get('body', ''),
                    'Confirmation': email_info.get('Confirmation', 'Unknown'),
                    'Num_trades': email_info.get('Num_trades', len(trades))
                }
                
                if trades:
                    # Create one record per trade (flattened structure)
                    for i, trade in enumerate(trades):
                        trade_record = {
                            **base_email_fields,
                            # Create unique ID for each trade within the email
                            'id': f"{email_id}_trade_{i}",
                            'tradeIndex': i,
                            
                            # Trade-specific fields from LLM extraction
                            'BankTradeNumber': trade.get('BankTradeNumber', ''),
                            'CounterpartyName': trade.get('CounterpartyName', ''),
                            'ProductType': trade.get('ProductType', ''),
                            'TradeDate': trade.get('TradeDate', ''),
                            'ValueDate': trade.get('ValueDate', ''),
                            'Direction': trade.get('Direction', ''),
                            'Currency1': trade.get('Currency1', ''),
                            'QuantityCurrency1': trade.get('QuantityCurrency1', 0),
                            'Currency2': trade.get('Currency2', ''),
                            'QuantityCurrency2': trade.get('QuantityCurrency2', 0),
                            'ExchangeRate': trade.get('ExchangeRate', 0),
                            'MaturityDate': trade.get('MaturityDate', ''),
                            'Price': trade.get('Price', 0),
                            'FixingReference': trade.get('FixingReference', ''),
                            'SettlementType': trade.get('SettlementType', ''),
                            'SettlementCurrency': trade.get('SettlementCurrency', ''),
                            'PaymentDate': trade.get('PaymentDate', ''),
                            'CounterpartyPaymentMethod': trade.get('CounterpartyPaymentMethod', ''),
                            'OurPaymentMethod': trade.get('OurPaymentMethod', ''),
                            'settlementInstructionStoragePath': trade.get('settlementInstructionStoragePath', ''),
                            'settlementInstructionError': trade.get('settlementInstructionError', ''),
                        }
                        
                        # First check if this trade has a match_id stored directly in it
                        trade_match_id = trade.get('match_id')
                        if trade_match_id:
                            # This trade already has a match_id stored in the email document
                            trade_record['matchId'] = trade_match_id
                            # Use the actual confirmation status stored on the trade
                            trade_record['status'] = trade.get('status', 'Confirmation OK')  # Use stored status or default
                            trade_record['matchStatus'] = 'matched'
                            
                        # Otherwise, check if this email has any matches (for backward compatibility)
                        else:
                            match_found = False
                            best_match = None
                            
                            if email_matches:
                                # If there are matches for this email, find the best one for this specific trade
                                # For now, use the first available match (could be improved with better matching logic)
                                for trade_number, match_info in email_matches.items():
                                    # For simplicity, assume first match corresponds to first email trade
                                    # This could be improved by matching based on trade characteristics
                                    best_match = match_info
                                    match_found = True
                                    break
                        
                            if match_found and best_match:
                                # Compare fields to determine if it's "Confirmation OK" or "Difference"
                                status, differing_fields = self._compare_trade_fields(trade, best_match['clientTradeData'])
                                
                                # Note: Duplicate detection happens during the matching process
                                # If an email trade would match a client trade that's already matched,
                                # no match record gets created, so duplicates will show as 'Unrecognized'
                                # We could enhance this later to detect and mark true duplicates
                                
                                trade_record.update({
                                    'matchId': best_match['matchId'],
                                    'status': status,
                                    'matchStatus': best_match['matchStatus'],
                                    'confidenceScore': best_match['confidenceScore'],
                                    'matchReasons': best_match['matchReasons'],
                                    'differingFields': differing_fields
                                })
                                # Remove this match so it's not reused for other email trades
                                email_matches.pop(next(iter(email_matches)), None)
                            else:
                                # Check if this email has been marked as containing duplicates
                                if email_data.get('hasDuplicates', False):
                                    trade_record.update({
                                        'status': 'Duplicate',
                                        'matchStatus': 'duplicate',
                                        'duplicateInfo': email_data.get('duplicateInfo', {})
                                    })
                                else:
                                    trade_record.update({
                                        'status': 'Unrecognized',
                                        'matchStatus': 'unmatched'
                                    })
                        
                        flattened_records.append(trade_record)
                else:
                    # Email with no trades extracted - create single record
                    email_record = {
                        **base_email_fields,
                        'status': 'Unrecognized',
                        'matchStatus': 'unmatched',
                        # Empty trade fields
                        'BankTradeNumber': '',
                        'CounterpartyName': '',
                        'ProductType': '',
                        'TradeDate': '',
                        'ValueDate': '',
                        'Direction': '',
                        'Currency1': '',
                        'QuantityCurrency1': 0,
                        'Currency2': '',
                        'QuantityCurrency2': 0,
                        'ExchangeRate': 0,
                        'MaturityDate': '',
                        'Price': 0,
                        'FixingReference': '',
                        'SettlementType': '',
                        'SettlementCurrency': '',
                        'PaymentDate': '',
                        'CounterpartyPaymentMethod': '',
                        'OurPaymentMethod': '',
                    }
                    
                    flattened_records.append(email_record)
            
            logger.info(f"Retrieved {len(flattened_records)} trade records from email confirmations for client {client_id}")
            return flattened_records
        except Exception as e:
            logger.error(f"Error getting email confirmations for client {client_id}: {e}")
            return []
    
    async def create_match(self, client_id: str, trade_id: str, email_id: str, 
                          confidence_score: int, match_reasons: List[str], 
                          match_id: str = None, bank_trade_number: str = None, 
                          status: str = None, counterparty_name: str = None,
                          trade_comparison_result: Tuple[str, List[str]] = None,
                          email_trade_data: Dict[str, Any] = None,
                          client_trade_data: Dict[str, Any] = None) -> bool:
        """Create a trade-email match and update email document with match_id and status"""
        try:
            # Generate match_id if not provided (for backward compatibility)
            if not match_id:
                match_id = str(uuid.uuid4())
            
            logger.info(f"📝 Creating new match: client_id={client_id}, trade_id={trade_id}, email_id={email_id}, confidence={confidence_score}%, match_id={match_id}, bank_trade_number={bank_trade_number}")
            matches_ref = self.db.collection('clients').document(client_id).collection('matches')
            
            match_doc = {
                'matchId': match_id,  # Store the unique match identifier
                'tradeId': trade_id,
                'emailId': email_id,
                'confidenceScore': confidence_score,
                'matchReasons': match_reasons,
                'status': 'confirmed' if confidence_score >= 90 else 'review_needed',
                'createdAt': datetime.now(),
                'organizationId': client_id
            }
            
            logger.debug(f"📝 Match document to create: {match_doc}")
            
            # Create match record (this will auto-create the collection if it doesn't exist)
            doc_ref = matches_ref.add(match_doc)
            logger.info(f"✅ Successfully created match with ID: {doc_ref[1].id} in collection clients/{client_id}/matches")
            
            # Update trade and email status
            await self._update_trade_status(client_id, trade_id, 'matched')
            await self._update_email_status(client_id, email_id, 'matched')
            
            # Update the specific trade in the email document with the match_id and status
            if bank_trade_number:
                await self._update_email_trade_match_id(client_id, email_id, bank_trade_number, match_id, status)
            
            # Schedule automated emails based on client settings and match result
            if trade_comparison_result:
                match_data = {
                    "match_id": match_id,
                    "trade_id": trade_id,
                    "email_id": email_id,
                    "confidence_score": confidence_score,
                    "bank_trade_number": bank_trade_number or "",
                    "counterparty_name": counterparty_name or "Unknown",
                    "email_trade_data": email_trade_data,  # Include full email trade data
                    "client_trade_data": client_trade_data  # Include full client trade data
                }
                
                await self.schedule_automation_emails(
                    client_id=client_id,
                    match_data=match_data,
                    trade_comparison_result=trade_comparison_result
                )
            else:
                logger.info("No trade comparison result provided, skipping email automation")
            
            logger.info(f"Created match between trade {trade_id} and email {email_id} with {confidence_score}% confidence")
            return True
        except Exception as e:
            logger.error(f"Error creating match for client {client_id}: {e}")
            return False
    
    async def check_existing_match(self, client_id: str, trade_id: str) -> Optional[Dict[str, Any]]:
        """
        Check if a client trade already has an existing match
        
        Args:
            client_id: ID of the client
            trade_id: ID of the client trade to check
            
        Returns:
            Match document if exists, None otherwise
        """
        try:
            logger.debug(f"🔎 Querying matches collection: clients/{client_id}/matches where tradeId=={trade_id}")
            matches_ref = self.db.collection('clients').document(client_id).collection('matches')
            query = matches_ref.where('tradeId', '==', trade_id).limit(1)
            docs = query.stream()
            
            match_docs = list(docs)
            logger.debug(f"🔎 Query returned {len(match_docs)} documents")
            
            if match_docs:
                match_data = match_docs[0].to_dict()
                match_data['id'] = match_docs[0].id
                logger.info(f"✅ Found existing match for trade {trade_id}: Match ID {match_data['id']}")
                return match_data
            
            logger.debug(f"✅ No existing match found for trade {trade_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error checking existing match for trade {trade_id}: {e}")
            return None
    
    async def mark_email_as_duplicate(self, client_id: str, email_id: str, 
                                     duplicate_trade_id: str, duplicate_trade_number: str,
                                     existing_match_id: str):
        """
        Mark an email as containing duplicate trades
        
        Args:
            client_id: ID of the client
            email_id: ID of the email document
            duplicate_trade_id: ID of the client trade that was already matched
            duplicate_trade_number: Trade number for logging
            existing_match_id: ID of the existing match record
        """
        try:
            email_ref = self.db.collection('clients').document(client_id).collection('emails').document(email_id)
            
            # Update email document with duplicate information
            email_ref.update({
                'hasDuplicates': True,
                'duplicateInfo': {
                    'duplicateTradeId': duplicate_trade_id,
                    'duplicateTradeNumber': duplicate_trade_number,
                    'existingMatchId': existing_match_id,
                    'detectedAt': datetime.now(),
                },
                'updatedAt': datetime.now()
            })
            
            logger.info(f"Marked email {email_id} as containing duplicates (Trade: {duplicate_trade_number})")
            
        except Exception as e:
            logger.error(f"Error marking email {email_id} as duplicate: {e}")
    
    async def get_upload_session(self, client_id: str, session_id: str) -> Optional[UploadSession]:
        """Get upload session by ID"""
        try:
            session_doc = (self.db.collection('clients').document(client_id)
                          .collection('uploadSessions').document(session_id).get())
            
            if not session_doc.exists:
                return None
            
            session_data = session_doc.to_dict()
            session_data['id'] = session_doc.id
            return UploadSession(**session_data)
        except Exception as e:
            logger.error(f"Error getting upload session {session_id} for client {client_id}: {e}")
            return None
    
    async def create_upload_session(self, client_id: str, file_name: str, file_type: str, 
                                   file_size: int, uploaded_by: str) -> str:
        """Create new upload session"""
        try:
            sessions_ref = self.db.collection('clients').document(client_id).collection('uploadSessions')
            
            session_doc = {
                'fileName': file_name,
                'fileType': file_type,
                'fileSize': file_size,
                'recordsProcessed': 0,
                'recordsFailed': 0,
                'status': 'processing',
                'uploadedBy': uploaded_by,
                'organizationId': client_id,
                'createdAt': datetime.now()
            }
            
            doc_ref = sessions_ref.add(session_doc)[1]
            logger.info(f"Created upload session {doc_ref.id} for file {file_name}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Error creating upload session for client {client_id}: {e}")
            return None
    
    async def update_upload_session(self, client_id: str, session_id: str, 
                                   records_processed: int, records_failed: int, 
                                   status: str, error_message: str = None) -> bool:
        """Update upload session progress"""
        try:
            session_ref = (self.db.collection('clients').document(client_id)
                          .collection('uploadSessions').document(session_id))
            
            update_data = {
                'recordsProcessed': records_processed,
                'recordsFailed': records_failed,
                'status': status,
                'updatedAt': datetime.now()
            }
            
            if error_message:
                update_data['errorMessage'] = error_message
            
            session_ref.update(update_data)
            return True
        except Exception as e:
            logger.error(f"Error updating upload session {session_id} for client {client_id}: {e}")
            return False
    
    async def _update_trade_status(self, client_id: str, trade_id: str, status: str):
        """Update trade status"""
        try:
            trade_ref = self.db.collection('clients').document(client_id).collection('trades').document(trade_id)
            trade_ref.update({'status': status, 'updatedAt': datetime.now()})
        except Exception as e:
            logger.error(f"Error updating trade status for {trade_id}: {e}")
    
    async def _update_email_status(self, client_id: str, email_id: str, status: str):
        """Update email status"""
        try:
            email_ref = self.db.collection('clients').document(client_id).collection('emails').document(email_id)
            email_ref.update({'status': status, 'updatedAt': datetime.now()})
        except Exception as e:
            logger.error(f"Error updating email status for {email_id}: {e}")
    
    async def _update_email_trade_match_id(self, client_id: str, email_id: str, 
                                          bank_trade_number: str, match_id: str, status: str = None):
        """Update a specific trade within an email document with match_id and status"""
        try:
            email_ref = self.db.collection('clients').document(client_id).collection('emails').document(email_id)
            
            # Get the email document
            email_doc = email_ref.get()
            if not email_doc.exists:
                logger.error(f"Email document {email_id} not found")
                return
            
            email_data = email_doc.to_dict()
            
            # Get the LLM extracted data
            llm_data = email_data.get('llmExtractedData', {})
            trades = llm_data.get('Trades', [])
            
            # Find and update the specific trade by BankTradeNumber
            trade_found = False
            for i, trade in enumerate(trades):
                if trade.get('BankTradeNumber') == bank_trade_number:
                    # Add match_id and status to this specific trade
                    trades[i]['match_id'] = match_id
                    if status:
                        trades[i]['status'] = status
                    trade_found = True
                    logger.info(f"✅ Added match_id {match_id} and status '{status}' to trade {bank_trade_number} in email {email_id}")
                    break
            
            if not trade_found:
                logger.warning(f"Trade with BankTradeNumber {bank_trade_number} not found in email {email_id}")
                return
            
            # Update the email document with modified trades array
            email_ref.update({
                'llmExtractedData.Trades': trades,
                'updatedAt': datetime.now()
            })
            
            logger.info(f"Successfully updated email {email_id} trade {bank_trade_number} with match_id {match_id} and status '{status}'")
            
        except Exception as e:
            logger.error(f"Error updating email trade match_id and status for {email_id}: {e}")
    
    # ========== CSV Upload Methods ==========
    
    async def process_csv_upload(self, client_id: str, csv_content: str, 
                                overwrite_existing: bool, uploaded_by: str, 
                                filename: str) -> Dict[str, Any]:
        """Process CSV upload and insert trade data"""
        try:
            # Parse CSV content
            trades, parsing_errors = self.csv_parser.parse_csv_content(csv_content)
            
            if parsing_errors:
                logger.warning(f"CSV parsing errors for client {client_id}: {parsing_errors}")
            
            # Validate required fields
            validation_errors = self.csv_parser.validate_required_fields(trades)
            if validation_errors:
                return {
                    'success': False,
                    'errors': validation_errors,
                    'records_processed': 0,
                    'records_failed': len(validation_errors)
                }
            
            # Create upload session
            session_id = await self.create_upload_session(
                client_id=client_id,
                file_name=filename,
                file_type="trades",
                file_size=len(csv_content),
                uploaded_by=uploaded_by
            )
            
            records_processed = 0
            records_failed = len(parsing_errors)
            
            # Process trades
            if trades:
                # If overwrite is true, delete existing unmatched trades
                if overwrite_existing:
                    await self._delete_unmatched_trades(client_id)
                    logger.info(f"Deleted existing unmatched trades for client {client_id}")
                
                # Insert new trades
                success_count = await self._insert_trades_batch(client_id, trades, session_id)
                records_processed = success_count
                records_failed += (len(trades) - success_count)
            
            # Update upload session
            session_status = "completed" if records_failed == 0 else "completed_with_errors"
            await self.update_upload_session(
                client_id=client_id,
                session_id=session_id,
                records_processed=records_processed,
                records_failed=records_failed,
                status=session_status
            )
            
            logger.info(f"CSV upload complete for client {client_id}: {records_processed} processed, {records_failed} failed")
            
            return {
                'success': True,
                'upload_session_id': session_id,
                'file_name': filename,
                'records_processed': records_processed,
                'records_failed': records_failed,
                'parsing_errors': parsing_errors,
                'overwrite_applied': overwrite_existing,
                'message': f"Successfully processed {records_processed} trades" + 
                          (f" with {records_failed} errors" if records_failed > 0 else "")
            }
            
        except Exception as e:
            logger.error(f"Error processing CSV upload for client {client_id}: {e}")
            return {
                'success': False,
                'errors': [str(e)],
                'records_processed': 0,
                'records_failed': 0
            }
    
    async def delete_all_unmatched_trades(self, client_id: str, deleted_by: str) -> int:
        """
        Public method to delete all unmatched trades for a client
        
        Args:
            client_id: ID of the client
            deleted_by: UID of the user performing the deletion
            
        Returns:
            Number of trades deleted
        """
        try:
            # Use the existing private method
            deleted_count = await self._delete_unmatched_trades(client_id)
            
            # Log the deletion action with user info
            logger.info(f"User {deleted_by} deleted {deleted_count} unmatched trades for client {client_id}")
            
            return deleted_count
        except Exception as e:
            logger.error(f"Error in public delete method for client {client_id}: {e}")
            raise e

    async def _delete_unmatched_trades(self, client_id: str) -> int:
        """Delete all unmatched trades for a client"""
        try:
            trades_ref = self.db.collection('clients').document(client_id).collection('trades')
            
            # First, let's see what trades exist and their status values
            all_docs = trades_ref.stream()
            all_trades_info = []
            for doc in all_docs:
                trade_data = doc.to_dict()
                all_trades_info.append({
                    'id': doc.id,
                    'status': trade_data.get('status', 'NO_STATUS_FIELD'),
                    'trade_number': trade_data.get('TradeNumber', 'NO_TRADE_NUMBER')
                })
            
            logger.info(f"Found {len(all_trades_info)} total trades for client {client_id}")
            for trade in all_trades_info:
                logger.info(f"Trade {trade['id']}: status='{trade['status']}', trade_number='{trade['trade_number']}'")
            
            # Now delete trades with status 'unmatched'
            query = trades_ref.where('status', '==', 'unmatched')
            docs = query.stream()
            
            deleted_count = 0
            for doc in docs:
                logger.info(f"Deleting trade {doc.id} with status 'unmatched'")
                doc.reference.delete()
                deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} unmatched trades for client {client_id}")
            return deleted_count
        except Exception as e:
            logger.error(f"Error deleting unmatched trades for client {client_id}: {e}")
            return 0
    
    async def _insert_trades_batch(self, client_id: str, trades: List[Dict[str, Any]], 
                                  session_id: str) -> int:
        """Insert trades in batch with error handling"""
        try:
            trades_ref = self.db.collection('clients').document(client_id).collection('trades')
            success_count = 0
            
            for trade in trades:
                try:
                    # Add metadata
                    trade_doc = {
                        **trade,
                        'uploadSessionId': session_id,
                        'organizationId': client_id,
                        'createdAt': datetime.now()
                    }
                    
                    trades_ref.add(trade_doc)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to insert trade {trade.get('TradeNumber', 'unknown')}: {e}")
            
            logger.info(f"Successfully inserted {success_count} trades for client {client_id}")
            return success_count
            
        except Exception as e:
            logger.error(f"Error inserting trades batch for client {client_id}: {e}")
            return 0
    
    async def process_email_upload(self, client_id: str, email_data: Dict[str, Any], 
                                   session_id: str, uploaded_by: str, filename: str) -> Dict[str, Any]:
        """
        Process uploaded email data and save to database
        
        Args:
            client_id: ID of the client
            email_data: Parsed email data from EmailParserService
            session_id: Upload session ID
            uploaded_by: UID of the user uploading
            filename: Original filename
            
        Returns:
            Processing result with email_id and other metadata
        """
        try:
            # Extract email metadata and LLM data
            email_metadata = email_data.get('email_metadata', {})
            llm_extracted_data = email_data.get('llm_extracted_data', {})
            
            # Log the processed email data for debugging
            logger.info(f"Processing email data for client {client_id}:")
            logger.info(f"  Email metadata: {email_metadata}")
            logger.info(f"  LLM extracted data: {llm_extracted_data}")
            
            # Save email confirmation record
            email_id = await self._save_email_confirmation(
                client_id=client_id,
                email_metadata=email_metadata,
                llm_extracted_data=llm_extracted_data,
                session_id=session_id,
                filename=filename
            )
            
            logger.info(f"Saved email confirmation {email_id} for client {client_id}")
            
            return {
                'email_id': email_id,
                'trades_extracted': len(llm_extracted_data.get('Trades', [])),
                'confirmation_detected': llm_extracted_data.get('Email', {}).get('Confirmation') == 'Yes',
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing email upload for client {client_id}: {e}")
            raise e
    
    async def _save_email_confirmation(self, client_id: str, email_metadata: Dict[str, Any], 
                                       llm_extracted_data: Dict[str, Any], session_id: str, 
                                       filename: str) -> str:
        """
        Save email confirmation to database
        
        Args:
            client_id: ID of the client
            email_metadata: Raw email metadata
            llm_extracted_data: LLM extracted structured data
            session_id: Upload session ID
            filename: Original filename
            
        Returns:
            Email document ID
        """
        try:
            emails_ref = self.db.collection('clients').document(client_id).collection('emails')
            
            
            # Create email document
            email_doc = {
                # Email metadata
                'senderEmail': email_metadata.get('sender_email', ''),
                'subject': email_metadata.get('subject', ''),
                'bodyContent': email_metadata.get('body_content', ''),
                'emailDate': email_metadata.get('date', ''),
                'emailTime': email_metadata.get('time', ''),
                'attachmentsText': email_metadata.get('attachments_text', ''),
                
                # LLM extracted data
                'llmExtractedData': llm_extracted_data,
                'confirmationDetected': llm_extracted_data.get('Email', {}).get('Confirmation') == 'Yes',
                'tradesCount': llm_extracted_data.get('Email', {}).get('Num_trades', 0),
                
                # Processing metadata
                'status': 'unmatched',  # Initial status
                'uploadSessionId': session_id,
                'filename': filename,
                'organizationId': client_id,
                'createdAt': datetime.now(),
                'processedAt': datetime.now()
            }
            
            # Add document and return ID
            doc_ref = emails_ref.add(email_doc)[1]
            
            
            return doc_ref.id
            
        except Exception as e:
            logger.error(f"Error saving email confirmation for client {client_id}: {e}")
            raise e
    
    def _compare_trade_fields(self, email_trade: Dict[str, Any], client_trade: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Compare ALL email trade fields with client trade fields to determine status
        Returns tuple: (status, list_of_differing_field_names)
        """
        try:
            differences = []
            differing_fields = []
            
            # 1. Product Type
            email_product = str(email_trade.get('ProductType', '')).strip()
            client_product = str(client_trade.get('ProductType', '')).strip()
            if email_product.upper() != client_product.upper():
                differences.append(f"ProductType: '{email_product}' vs '{client_product}'")
                differing_fields.append('ProductType')
            
            # 2. Trade Date
            email_trade_date = self._normalize_date(email_trade.get('TradeDate', ''))
            client_trade_date = self._normalize_date(client_trade.get('TradeDate', ''))
            if email_trade_date != client_trade_date:
                differences.append(f"TradeDate: '{email_trade.get('TradeDate')}' vs '{client_trade.get('TradeDate')}'")
                differing_fields.append('TradeDate')
            
            # 3. Value Date
            email_value_date = self._normalize_date(email_trade.get('ValueDate', ''))
            client_value_date = self._normalize_date(client_trade.get('ValueDate', ''))
            if email_value_date != client_value_date:
                differences.append(f"ValueDate: '{email_trade.get('ValueDate')}' vs '{client_trade.get('ValueDate')}'")
                differing_fields.append('ValueDate')
            
            # 4. Direction
            email_direction = str(email_trade.get('Direction', '')).strip()
            client_direction = str(client_trade.get('Direction', '')).strip()
            if email_direction.upper() != client_direction.upper():
                differences.append(f"Direction: '{email_direction}' vs '{client_direction}'")
                differing_fields.append('Direction')
            
            # 5. Currency 1
            email_cur1 = str(email_trade.get('Currency1', '')).strip()
            client_cur1 = str(client_trade.get('Currency1', '')).strip()
            if email_cur1.upper() != client_cur1.upper():
                differences.append(f"Currency1: '{email_cur1}' vs '{client_cur1}'")
                differing_fields.append('Currency1')
            
            # 6. Amount (Quantity Currency 1) - exact match
            email_amount = float(email_trade.get('QuantityCurrency1', 0))
            client_amount = float(client_trade.get('QuantityCurrency1', 0))
            if email_amount != client_amount:
                differences.append(f"QuantityCurrency1: {email_amount} vs {client_amount}")
                differing_fields.append('QuantityCurrency1')
            
            # 7. Price - exact match
            email_price = float(email_trade.get('Price', 0))
            client_price = float(client_trade.get('Price', 0))
            if email_price != client_price:
                differences.append(f"Price: {email_price} vs {client_price}")
                differing_fields.append('Price')
            
            # 8. Currency 2
            email_cur2 = str(email_trade.get('Currency2', '')).strip()
            client_cur2 = str(client_trade.get('Currency2', '')).strip()
            if email_cur2.upper() != client_cur2.upper():
                differences.append(f"Currency2: '{email_cur2}' vs '{client_cur2}'")
                differing_fields.append('Currency2')
            
            # 9. Maturity Date
            email_maturity = self._normalize_date(email_trade.get('MaturityDate', ''))
            client_maturity = self._normalize_date(client_trade.get('MaturityDate', ''))
            if email_maturity != client_maturity:
                differences.append(f"MaturityDate: '{email_trade.get('MaturityDate')}' vs '{client_trade.get('MaturityDate')}'")
                differing_fields.append('MaturityDate')
            
            # 10. Fixing Reference
            email_fixing = str(email_trade.get('FixingReference', '')).strip()
            client_fixing = str(client_trade.get('FixingReference', '')).strip()
            if email_fixing.upper() != client_fixing.upper():
                differences.append(f"FixingReference: '{email_fixing}' vs '{client_fixing}'")
                differing_fields.append('FixingReference')
            
            # 11. Settlement Type
            email_settlement_type = str(email_trade.get('SettlementType', '')).strip()
            client_settlement_type = str(client_trade.get('SettlementType', '')).strip()
            if email_settlement_type.upper() != client_settlement_type.upper():
                differences.append(f"SettlementType: '{email_settlement_type}' vs '{client_settlement_type}'")
                differing_fields.append('SettlementType')
            
            # 12. Settlement Currency
            email_settlement_cur = str(email_trade.get('SettlementCurrency', '')).strip()
            client_settlement_cur = str(client_trade.get('SettlementCurrency', '')).strip()
            if email_settlement_cur.upper() != client_settlement_cur.upper():
                differences.append(f"SettlementCurrency: '{email_settlement_cur}' vs '{client_settlement_cur}'")
                differing_fields.append('SettlementCurrency')
            
            # 13. Payment Date
            email_payment_date = self._normalize_date(email_trade.get('PaymentDate', ''))
            client_payment_date = self._normalize_date(client_trade.get('PaymentDate', ''))
            if email_payment_date != client_payment_date:
                differences.append(f"PaymentDate: '{email_trade.get('PaymentDate')}' vs '{client_trade.get('PaymentDate')}'")
                differing_fields.append('PaymentDate')
            
            # 14. Our Payment Method
            email_our_method = str(email_trade.get('OurPaymentMethod', '')).strip()
            client_our_method = str(client_trade.get('OurPaymentMethod', '')).strip()
            if email_our_method.upper() != client_our_method.upper():
                differences.append(f"OurPaymentMethod: '{email_our_method}' vs '{client_our_method}'")
                differing_fields.append('OurPaymentMethod')
            
            # 15. Counterparty Payment Method
            email_cp_method = str(email_trade.get('CounterpartyPaymentMethod', '')).strip()
            client_cp_method = str(client_trade.get('CounterpartyPaymentMethod', '')).strip()
            if email_cp_method.upper() != client_cp_method.upper():
                differences.append(f"CounterpartyPaymentMethod: '{email_cp_method}' vs '{client_cp_method}'")
                differing_fields.append('CounterpartyPaymentMethod')
            
            # Result: ALL fields must match for "Confirmation OK"
            if not differences:
                logger.info("All trade fields match - Confirmation OK")
                return ('Confirmation OK', [])
            else:
                logger.info(f"Trade differences found ({len(differences)} fields): {', '.join(differences[:3])}{'...' if len(differences) > 3 else ''}")
                return ('Difference', differing_fields)
                
        except Exception as e:
            logger.warning(f"Error comparing trade fields: {e}")
            return ('Difference', [])  # Default to difference if comparison fails
    
    def _normalize_date(self, date_str: str) -> str:
        """
        Normalize date string to DD-MM-YYYY format for comparison
        """
        if not date_str:
            return ''
        
        # Handle different date formats
        date_str = str(date_str).strip()
        
        # If already in DD-MM-YYYY format, return as-is
        if re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):
            return date_str
        
        # Handle other common formats and convert to DD-MM-YYYY
        # This is a simplified version - could be expanded based on actual data formats
        try:
            from datetime import datetime
            # Try parsing common formats
            for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y']:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    return parsed_date.strftime('%d-%m-%Y')
                except ValueError:
                    continue
        except:
            pass
        
        return date_str  # Return original if can't parse
    
    async def get_email_confirmations(self, client_id: str) -> List[Dict[str, Any]]:
        """
        Get all email confirmations for a client
        
        Args:
            client_id: ID of the client
            
        Returns:
            List of email confirmations
        """
        try:
            emails_ref = self.db.collection('clients').document(client_id).collection('emails')
            docs = emails_ref.stream()
            
            emails = []
            for doc in docs:
                raw_email_data = doc.to_dict()
                
                # Convert Firestore timestamps to strings
                created_at = raw_email_data.get('createdAt', '')
                if hasattr(created_at, 'strftime'):
                    created_at = created_at.strftime('%Y-%m-%d %H:%M:%S')
                
                # Start with basic email data structure
                email_data = {
                    'id': doc.id,
                    'status': raw_email_data.get('status', 'unmatched'),
                    'createdAt': created_at,
                }
                
                # Add email fields from LLM data
                # First add any LLM extracted email fields
                if email_section:
                    email_data.update({
                        'EmailSubject': email_section.get('EmailSubject', ''),
                        'EmailSender': email_section.get('EmailSender', ''),
                    })
                
                # Override with actual metadata from root level (these are the source of truth)
                email_data.update({
                    'EmailSender': raw_email_data.get('senderEmail', ''),  # Override with actual metadata
                    'EmailSubject': raw_email_data.get('subject', ''),  # Override with actual metadata
                    'EmailDate': raw_email_data.get('emailDate', ''),  # Use root-level metadata date
                    'EmailTime': raw_email_data.get('emailTime', ''),  # Use root-level metadata time
                })
                
                
                # Add first trade data from LLM results if available (these now have correct field names)
                trades = llm_data.get('Trades', [])
                if trades and len(trades) > 0:
                    first_trade = trades[0]
                    email_data.update(first_trade)  # Direct copy since field names now match
                    
                else:
                    # Add empty trade fields if no trades found
                    email_data.update({
                        'BankTradeNumber': '',
                        'CounterpartyName': '',
                        'ProductType': '',
                        'Direction': '',
                        'Currency1': '',
                        'QuantityCurrency1': 0.0,
                        'Currency2': '',
                        'TradeDate': '',
                        'ValueDate': '',
                        'MaturityDate': '',
                        'Price': 0.0,
                        'FixingReference': '',
                        'SettlementType': '',
                        'SettlementCurrency': '',
                        'PaymentDate': '',
                        'CounterpartyPaymentMethod': '',
                        'OurPaymentMethod': '',
                        'differingFields': []
                    })
                
                emails.append(email_data)
            
            # Sort by creation date (newest first)
            emails.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
            
            logger.info(f"Retrieved {len(emails)} email confirmations for client {client_id}")
            
            # Log the first email for debugging (if any exist)
            if emails:
                logger.info(f"First email sample: {emails[0]}")
            
            return emails
            
        except Exception as e:
            logger.error(f"Error getting email confirmations for client {client_id}: {e}")
            return []
    
    # ========== Email Automation Methods ==========
    
    async def schedule_automation_emails(self, client_id: str, match_data: Dict[str, Any], 
                                       trade_comparison_result: Tuple[str, List[str]]) -> bool:
        """
        Schedule automated confirmation or dispute emails based on client settings
        
        Args:
            client_id: ID of the client
            match_data: Dictionary containing match information (trade_id, email_id, etc.)
            trade_comparison_result: Tuple from _compare_trade_fields (status, differing_fields)
            
        Returns:
            bool: True if email was scheduled successfully
        """
        try:
            # Get client automation settings
            client_settings = await self.get_client_settings(client_id)
            if not client_settings:
                logger.info(f"No automation settings found for client {client_id}, skipping email automation")
                return False
            
            automation_settings = client_settings.automation
            comparison_status, differing_fields = trade_comparison_result
            
            # Determine email type and settings based on comparison result
            if comparison_status == "Confirmation OK":
                # Perfect match - check auto_confirm_matched settings
                email_settings = automation_settings.auto_confirm_matched
                email_type = "confirmation"
                logger.info(f"Trade matched perfectly - checking confirmation email automation")
            else:
                # Differences found - check auto_confirm_disputed settings  
                email_settings = automation_settings.auto_confirm_disputed
                email_type = "dispute"
                logger.info(f"Trade has {len(differing_fields)} differences - checking dispute email automation")
            
            # Check if automation is enabled for this email type
            if not email_settings.enabled:
                logger.info(f"Email automation disabled for {email_type} emails in client {client_id}")
                return False
            
            # Get delay from client settings (convert minutes to seconds)
            delay_seconds = email_settings.delay_minutes * 60
            logger.info(f"Scheduling {email_type} email with {delay_seconds} second delay ({email_settings.delay_minutes} minutes)")
            
            # Prepare email data for the task
            email_data = {
                "client_id": client_id,
                "match_id": match_data.get("match_id", ""),
                "trade_id": match_data.get("trade_id", ""),
                "email_id": match_data.get("email_id", ""),
                "email_type": email_type,
                "comparison_status": comparison_status,
                "differing_fields": differing_fields,
                "confidence_score": match_data.get("confidence_score", 0),
                "bank_trade_number": match_data.get("bank_trade_number", ""),
                "counterparty_name": match_data.get("counterparty_name", "Unknown"),
                "scheduled_at": datetime.now(timezone.utc).isoformat(),
                "email_trade_data": match_data.get("email_trade_data", {}),  # Include full email trade data
                "client_trade_data": match_data.get("client_trade_data", {})  # Include full client trade data
            }
            
            # Schedule the email task using our task queue service
            task_name = await auto_email_service.schedule_trade_email(
                email_data=email_data,
                delay_seconds=delay_seconds
            )
            
            if task_name:
                logger.info(f"✅ Successfully scheduled {email_type} email task: {task_name}")
            else:
                logger.error(f"❌ Failed to schedule {email_type} email task")
            
            # Also trigger SMS notifications if configured
            # SMS is sent immediately (no delay like emails)
            try:
                trade_data = match_data.get("client_trade_data", {})
                if not trade_data:
                    trade_data = match_data.get("email_trade_data", {})
                
                # Add trade number if not present
                if "TradeNumber" not in trade_data:
                    trade_data["TradeNumber"] = match_data.get("bank_trade_number", "Unknown")
                if "CounterpartyName" not in trade_data:
                    trade_data["CounterpartyName"] = match_data.get("counterparty_name", "Unknown")
                
                sms_result = await auto_sms_service.process_trade_sms_notifications(
                    client_id=client_id,
                    trade_status=comparison_status,
                    trade_data=trade_data,
                    discrepancies=differing_fields if comparison_status != "Confirmation OK" else None
                )
                
                if sms_result.get('sms_sent'):
                    logger.info(f"✅ SMS notifications sent for {email_type} trade")
                else:
                    logger.debug(f"No SMS sent (may be disabled or no phone numbers configured)")
                    
            except Exception as sms_error:
                logger.error(f"Error sending SMS notifications: {sms_error}")
                # Don't fail the whole process if SMS fails
            
            return task_name is not None
                
        except Exception as e:
            logger.error(f"Error scheduling automation emails for client {client_id}: {e}")
            return False

    # ========== Utility Methods ==========
    
    async def client_exists(self, client_id: str) -> bool:
        """Check if client exists"""
        try:
            client_doc = self.db.collection('clients').document(client_id).get()
            return client_doc.exists
        except Exception as e:
            logger.error(f"Error checking if client {client_id} exists: {e}")
            return False
    
    async def process_and_match_email(self, client_id: str, email_data: Dict[str, Any], 
                                      session_id: str, uploaded_by: str, filename: str) -> Optional[Dict[str, Any]]:
        """
        Unified email processing method that handles extraction, saving, and matching
        
        Args:
            client_id: ID of the client
            email_data: Parsed email data from EmailParserService
            session_id: Upload session ID
            uploaded_by: Who uploaded/processed this (e.g., 'gmail_service', 'user_uid')
            filename: Original filename
            
        Returns:
            Processing result with email_id, matching results, and statistics
        """
        try:
            # Step 1: Save the email using existing method
            result = await self.process_email_upload(
                client_id=client_id,
                email_data=email_data,
                session_id=session_id,
                uploaded_by=uploaded_by,
                filename=filename
            )
            
            if not result or not result.get('email_id'):
                logger.error(f"Failed to save email data for {filename}")
                return None
            
            # Step 2: Check if we should run matching
            llm_data = email_data.get('llm_extracted_data', {})
            extracted_trades_count = len(llm_data.get('Trades', []))
            is_confirmation = llm_data.get('Email', {}).get('Confirmation') == 'Yes'
            
            logger.info(f"Email processing - Trades: {extracted_trades_count}, Confirmation: {is_confirmation}")
            
            # Step 3: Auto-trigger matching if this is a trade confirmation with extracted trades
            matches_found = 0
            matched_trade_numbers = []
            duplicates_found = 0
            counterparty_name = 'Unknown'
            
            if extracted_trades_count > 0 and is_confirmation:
                logger.info(f"Auto-triggering matching for {filename} with {extracted_trades_count} trades")
                
                try:
                    # Import here to avoid circular imports
                    from services.matching_service import MatchingService
                    matching_service = MatchingService()
                    
                    # Get unmatched trades for matching
                    unmatched_trades = await self.get_unmatched_trades(client_id)
                    logger.info(f"Found {len(unmatched_trades)} unmatched trades for matching")
                    
                    if unmatched_trades:
                        # Prepare email trades and metadata for matching
                        email_trades = llm_data.get('Trades', [])
                        email_metadata = {
                            'sender_email': email_data.get('email_metadata', {}).get('sender_email', ''),
                            'subject': email_data.get('email_metadata', {}).get('subject', ''),
                            'date': email_data.get('email_metadata', {}).get('date', ''),
                        }
                        
                        # Run matching algorithm
                        match_results = matching_service.match_email_trades_with_client_trades(
                            email_trades, unmatched_trades, email_metadata
                        )
                        
                        # Process match results
                        for match_result in match_results:
                            if match_result['matched_client_trade'] is not None:
                                client_trade_id = match_result['matched_client_trade'].get('id', '')
                                client_trade_number = match_result['matched_client_trade'].get('TradeNumber', '')
                                
                                # Check for duplicates
                                logger.info(f"🔍 Checking for existing match: client_id={client_id}, trade_id={client_trade_id}, trade_number={client_trade_number}")
                                existing_match = await self.check_existing_match(client_id, client_trade_id)
                                logger.info(f"🔍 Existing match result: {existing_match}")
                                if existing_match:
                                    logger.warning(f"Duplicate detected - Trade {client_trade_number} already matched")
                                    await self.mark_email_as_duplicate(
                                        client_id=client_id,
                                        email_id=result['email_id'],
                                        duplicate_trade_id=client_trade_id,
                                        duplicate_trade_number=client_trade_number,
                                        existing_match_id=existing_match['id']
                                    )
                                    duplicates_found += 1
                                else:
                                    # Create the match
                                    logger.info(f"🆕 No existing match found - Creating new match for trade {client_trade_number}")
                                    # Extract bank trade number from the email trade
                                    bank_trade_number = match_result['email_trade'].get('BankTradeNumber', '')
                                    match_created = await self.create_match(
                                        client_id=client_id,
                                        trade_id=client_trade_id,
                                        email_id=result['email_id'],
                                        confidence_score=match_result['confidence'],
                                        match_reasons=match_result['match_reasons'],
                                        match_id=match_result['match_id'],  # Pass the generated match_id from MatchingService
                                        bank_trade_number=bank_trade_number,  # Pass bank trade number to update email doc
                                        status=match_result['status'],  # Pass the proper confirmation status from MatchingService
                                        counterparty_name=match_result['email_trade'].get('CounterpartyName', 'Unknown'),
                                        trade_comparison_result=(match_result['status'], match_result.get('discrepancies', [])),
                                        email_trade_data=match_result['email_trade'],  # Pass full email trade data
                                        client_trade_data=match_result['matched_client_trade']  # Pass full client trade data
                                    )
                                    
                                    if match_created:
                                        matches_found += 1
                                        matched_trade_numbers.append(client_trade_number)
                                        logger.info(f"✅ Successfully created match for trade {client_trade_number} with {match_result['confidence']}% confidence")
                                    else:
                                        logger.error(f"❌ Failed to create match for trade {client_trade_number}")
                                
                                # Extract counterparty name for summary
                                if counterparty_name == 'Unknown':
                                    counterparty_name = match_result['email_trade'].get('CounterpartyName', 'Unknown')
                    else:
                        logger.info("No unmatched trades available for matching")
                        
                except Exception as e:
                    logger.error(f"Error during matching process: {e}", exc_info=True)
            
            # Step 4: Return comprehensive result
            final_result = {
                **result,  # Include original result (email_id, trades_extracted, etc.)
                'matches_found': matches_found,
                'matched_trade_numbers': matched_trade_numbers,
                'duplicates_found': duplicates_found,
                'counterparty_name': counterparty_name,
                'matching_attempted': extracted_trades_count > 0 and is_confirmation,
                'processing_complete': True
            }
            
            logger.info(f"Email processing complete for {filename}: {matches_found} matches, {duplicates_found} duplicates")
            
            # Emit real-time event for Gmail processing
            if uploaded_by == 'gmail_service' and (matches_found > 0 or duplicates_found > 0 or extracted_trades_count > 0):
                try:
                    from services.event_service import event_service
                    
                    # Determine event message and action
                    if duplicates_found > 0:
                        event_title = "Email Processed (Duplicates Detected)"
                        event_message = f"⚠️ {duplicates_found} duplicates detected from {counterparty_name}. {matches_found} new matches created."
                        event_priority = 'medium'
                    elif matches_found > 0:
                        event_title = "Email Processed Successfully" 
                        event_message = f"✅ {matches_found} matches found from {counterparty_name}. Trades: {', '.join(matched_trade_numbers) if matched_trade_numbers else 'N/A'}"
                        event_priority = 'medium'
                    else:
                        event_title = "Email Processed (No Matches)"
                        event_message = f"📧 Email from {counterparty_name} processed but no matches found ({extracted_trades_count} trades extracted)."
                        event_priority = 'low'
                    
                    # Emit the event
                    await event_service.emit_event(
                        event_type='gmail_processed',
                        title=event_title,
                        message=event_message,
                        client_id=client_id,
                        priority=event_priority,
                        action='refresh_grids' if matches_found > 0 or duplicates_found > 0 else 'show_toast',
                        payload={
                            'filename': filename,
                            'matches_found': matches_found,
                            'duplicates_found': duplicates_found,
                            'trades_extracted': extracted_trades_count,
                            'counterparty_name': counterparty_name,
                            'matched_trade_numbers': matched_trade_numbers
                        }
                    )
                    
                    logger.info(f"📡 Emitted Gmail processing event: {event_title}")
                    
                except Exception as e:
                    logger.error(f"Failed to emit Gmail event: {e}")
                    # Don't fail the whole process if event emission fails
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in unified email processing for {filename}: {e}", exc_info=True)
            return None

    async def process_gmail_attachment(self, client_id: str, gmail_email_data: Dict[str, Any], 
                                      attachment_data: bytes, filename: str) -> Optional[Dict[str, Any]]:
        """
        Process Gmail attachment using unified email processing pipeline
        
        Args:
            client_id: ID of the client
            gmail_email_data: Gmail email metadata (sender, subject, date, body)
            attachment_data: PDF attachment content as bytes
            filename: Attachment filename
            
        Returns:
            Processing result with matching results
        """
        try:
            # Create a session ID for tracking
            session_id = f"gmail_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Get client name for context
            client_name = self.get_client_name(client_id)
            logger.info(f"ClientService: Got client_name '{client_name}' for client_id '{client_id}'")
            
            # Use existing EmailParserService to process the PDF attachment
            from services.email_parser import EmailParserService
            email_parser = EmailParserService()
            email_data, errors = email_parser.process_email_file(attachment_data, filename, client_name)
            
            if errors:
                logger.warning(f"Errors processing Gmail PDF {filename}: {errors}")
            
            if not email_data:
                logger.warning(f"No data extracted from Gmail PDF {filename}")
                return None
            
            # Override email metadata with Gmail data
            if 'email_metadata' in email_data:
                email_data['email_metadata'].update({
                    'sender_email': gmail_email_data.get('sender', ''),
                    'subject': gmail_email_data.get('subject', ''),
                    'date': gmail_email_data.get('date', ''),
                    'body_content': gmail_email_data.get('body', '')
                })
            
            # Use unified processing method
            logger.info(f"🔄 Calling unified process_and_match_email method for {filename}")
            result = await self.process_and_match_email(
                client_id=client_id,
                email_data=email_data,
                session_id=session_id,
                uploaded_by='gmail_service',
                filename=filename
            )
            
            logger.info(f"✅ Gmail processing completed for {filename}: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing Gmail attachment {filename} for client {client_id}: {e}")
            return None
    
    async def process_gmail_email_body(self, client_id: str, gmail_email_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process Gmail email body content directly when no PDF attachments are found
        
        Args:
            client_id: ID of the client
            gmail_email_data: Gmail email metadata including body content
            
        Returns:
            Processing result with matching results
        """
        try:
            # Create a session ID for tracking
            session_id = f"gmail_body_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create email data structure for LLM processing
            email_metadata = {
                'sender_email': gmail_email_data.get('sender', ''),
                'subject': gmail_email_data.get('subject', ''),
                'body_content': gmail_email_data.get('body', ''),
                'date': gmail_email_data.get('date', datetime.now().strftime('%d-%m-%Y')),
                'time': datetime.now().strftime('%H:%M:%S'),
                'attachments_text': ''  # No attachments since we're processing body
            }
            
            # Process email body with LLM to extract structured trade data
            from services.llm_service import LLMService
            llm_service = LLMService()
            
            formatted_email_data = {
                'subject': email_metadata['subject'],
                'body_content': email_metadata['body_content'],
                'sender_email': email_metadata['sender_email'],
                'attachments_text': ''
            }
            
            # Get client name for context
            client_name = self.get_client_name(client_id)
            logger.info(f"ClientService: Got client_name '{client_name}' for client_id '{client_id}' (email body processing)")
            
            logger.info(f"📝 Processing email body with LLM ({len(email_metadata['body_content'])} chars)")
            llm_extracted_data = llm_service.process_email_data(formatted_email_data, client_name)
            
            # Create the email data structure matching the expected format
            email_data = {
                'email_metadata': email_metadata,
                'llm_extracted_data': llm_extracted_data,
                'processed_at': datetime.now().isoformat(),
                'processing_source': 'email_body'
            }
            
            # Use unified processing method
            logger.info(f"🔄 Calling unified process_and_match_email method for email body")
            result = await self.process_and_match_email(
                client_id=client_id,
                email_data=email_data,
                session_id=session_id,
                uploaded_by='gmail_service',
                filename=f"email_body_{gmail_email_data.get('sender', 'unknown')[:20]}.txt"
            )
            
            logger.info(f"✅ Gmail body processing completed: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing Gmail email body for client {client_id}: {e}", exc_info=True)
            return None