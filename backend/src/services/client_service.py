"""
Client service for managing client settings and related data
"""

from typing import Optional, List, Dict, Any, Tuple
from google.cloud.firestore import DocumentReference, Query
import logging
import re
from datetime import datetime

from config.firebase_config import get_cmek_firestore_client
from services.csv_parser import CSVParserService
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
                'active': True,
                'createdAt': datetime.now(),
                'lastUpdatedAt': datetime.now(),
                'lastUpdatedBy': self.db.collection('users').document(created_by_uid)
            })
            
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
            for field, value in rule_update.dict(by_alias=True, exclude_none=True).items():
                update_data[field] = value
            
            # Add metadata
            update_data['lastUpdatedAt'] = datetime.now()
            update_data['lastUpdatedBy'] = self.db.collection('users').document(updated_by_uid)
            
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
                    trade_data['match_id'] = match_data.get('match_id', match_docs[0].id)
                    trade_data['match_confidence'] = f"{int(match_data.get('confidenceScore', 0) * 100)}%"
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
            docs = emails_ref.stream()  # Let frontend handle sorting
            
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
                                        'matchId': match_doc.id,
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
                            'ForwardPrice': trade.get('ForwardPrice', 0),
                            'FixingReference': trade.get('FixingReference', ''),
                            'SettlementType': trade.get('SettlementType', ''),
                            'SettlementCurrency': trade.get('SettlementCurrency', ''),
                            'PaymentDate': trade.get('PaymentDate', ''),
                            'CounterpartyPaymentMethod': trade.get('CounterpartyPaymentMethod', ''),
                            'OurPaymentMethod': trade.get('OurPaymentMethod', ''),
                        }
                        
                        # Check if this email has any matches and try to find the best match for this trade
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
                        'ForwardPrice': 0,
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
                          confidence_score: int, match_reasons: List[str]) -> bool:
        """Create a trade-email match"""
        try:
            matches_ref = self.db.collection('clients').document(client_id).collection('matches')
            
            match_doc = {
                'tradeId': trade_id,
                'emailId': email_id,
                'confidenceScore': confidence_score,
                'matchReasons': match_reasons,
                'status': 'confirmed' if confidence_score >= 90 else 'review_needed',
                'createdAt': datetime.now(),
                'organizationId': client_id
            }
            
            # Create match record
            matches_ref.add(match_doc)
            
            # Update trade and email status
            await self._update_trade_status(client_id, trade_id, 'matched')
            await self._update_email_status(client_id, email_id, 'matched')
            
            logger.info(f"Created match between trade {trade_id} and email {email_id} with {confidence_score}% confidence")
            return True
        except Exception as e:
            logger.error(f"Error creating match for client {client_id}: {e}")
            return False
    
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
            
            # 7. Price (Forward Price) - exact match
            email_price = float(email_trade.get('ForwardPrice', 0))
            client_price = float(client_trade.get('ForwardPrice', 0))
            if email_price != client_price:
                differences.append(f"ForwardPrice: {email_price} vs {client_price}")
                differing_fields.append('ForwardPrice')
            
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
                        'ForwardPrice': 0.0,
                        'FixingReference': '',
                        'SettlementType': '',
                        'SettlementCurrency': '',
                        'PaymentDate': '',
                        'CounterpartyPaymentMethod': '',
                        'OurPaymentMethod': ''
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
    
    # ========== Utility Methods ==========
    
    async def client_exists(self, client_id: str) -> bool:
        """Check if client exists"""
        try:
            client_doc = self.db.collection('clients').document(client_id).get()
            return client_doc.exists
        except Exception as e:
            logger.error(f"Error checking if client {client_id} exists: {e}")
            return False