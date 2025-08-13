# backend/app/services/confirmation_service.py
import asyncio
import os
import logging # Keep standard logging import for default logger
import json
import uuid
from datetime import datetime, UTC
import pandas as pd # Needed for _normalize_value if pd.Timestamp is used

# Use Config for LOGICAL_ASSET_PREFIX and storage adapter
from ..config import Config
from ..core.logger import logger # Your custom logger instance
# Assuming these are correctly imported from your custom logging package
from core_logging.client import EventType, LogLevel
# Assuming these are correctly imported from your email monitoring package
from email_monitoring.utils import clean_html, extract_dates
from typing import Optional, Dict, List, Union, Any # Ensure Any is imported

class ConfirmationService:
    def __init__(self, graph_client=None, llm_service=None, email_processor_service=None, logger=None):
        self.graph_client = graph_client
        self.llm_service = llm_service
        # Ensure the passed email_processor_service instance is the updated one
        self.email_processor = email_processor_service
        # self.assets_path = Config.ASSETS_PATH # Removed - use logical paths
        self.logger = logger or logging.getLogger(__name__) # Use passed logger or default standard logger
        self.my_entity = os.environ.get('MY_ENTITY', 'ConfirmationService') # Default entity name

        # Load mappings and entities on initialization using the corrected methods
        self.counterparty_mappings = self.load_counterparty_mappings()
        self.email_entities = self.load_email_entities()

        # Set up basic logging config *if* no logger was passed AND using default standard logger
        # This might be redundant if your main app configures logging globally
        # if not logger:
        #      logging.basicConfig(
        #          level=getattr(logging, Config.LOG_LEVEL, 'INFO'),
        #          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        #      )
        self.logger.info(f"{self.my_entity} initialized.")


    def load_email_entities(self, file_name="email_entities.json") -> List[Dict]:
        """Loads email entities using storage adapter and logical path."""
        # --- MODIFICATION: Use logical path ---
        logical_path = f"{Config.LOGICAL_ASSET_PREFIX}/{file_name}"
        # --- End Modification ---
        try:
            self.logger.info(f"Loading email entities from logical path: {logical_path}")

            # Read using storage adapter and LOGICAL PATH
            # read_json returns [] if not found or invalid
            entities = Config.storage.read_json(logical_path)
            if not isinstance(entities, list):
                 self.logger.error(f"Expected list from read_json for {logical_path}, got {type(entities)}. Returning empty list.")
                 return []

            self.logger.info(f"Loaded {len(entities)} email entities.")
            return entities
        except Exception as e:
            # --- MODIFICATION: Use log_exception ---
            # Use log_exception if self.logger is your custom client, otherwise use standard exception
            log_method = getattr(self.logger, 'log_exception', self.logger.log_exception)
            log_method(e, message=f"Failed to load email entities from {logical_path}")
            # --- End Modification ---
            return [] # Return empty list on error

    def get_entity_info(self, sender_email: str, email_entities: List[Dict]) -> tuple:
        """Get entity information from the loaded email entities list."""
        # No changes needed here, uses the passed list
        if not sender_email: # Handle empty sender email
             return None, None, None
        sender_email_lower = sender_email.lower()
        for entity in email_entities:
            # Check if 'email' key exists and is a string before lowercasing
            entity_email = entity.get('email')
            if isinstance(entity_email, str) and entity_email.lower() == sender_email_lower:
                return (
                    entity.get('entity_name'),
                    entity.get('entity_display_name', entity.get('entity_name')), # Fallback display name
                    entity.get('client_id', 'No ID')
                )
        return None, None, None # Return tuple of Nones

    def save_identified_trade(self, trade_data: dict, match_id=None, status: str = None, match_score: int = None, match_reasons: list = None) -> Optional[str]:
        """Save identified trade to matched_trades.json using logical path."""
        # --- MODIFICATION: Use logical path ---
        file_name = 'matched_trades.json'
        logical_path = f"{Config.LOGICAL_ASSET_PREFIX}/{file_name}"
        # --- End Modification ---

        try:
            # Generate a unique match_id if not provided
            if match_id is None:
                match_id = str(uuid.uuid4())
            else:
                 match_id = str(match_id) # Ensure string

            # Read existing matches using storage adapter and LOGICAL PATH
            matches = Config.storage.read_json(logical_path)
            if not isinstance(matches, list):
                 self.logger.error(f"Expected list from read_json for {logical_path}, got {type(matches)}. Cannot save trade.")
                 return None # Indicate failure

            # Add additional metadata to trade data
            trade_data_to_save = trade_data.copy() # Work on a copy
            trade_data_to_save['identified_at'] = datetime.now(UTC).isoformat()
            trade_data_to_save['match_id'] = match_id

            # Add status and confidence information if provided
            if status:
                trade_data_to_save['status'] = status

            if match_score is not None:
                # Calculate confidence as percentage (score out of total possible 90 points)
                # Avoid division by zero if match_score is somehow negative or zero incorrectly
                match_confidence = round((max(0, match_score) / 90) * 100) if match_score is not None else None
                if match_confidence is not None:
                     trade_data_to_save['match_confidence'] = f"{match_confidence}%"

            if match_reasons:
                trade_data_to_save['match_reasons'] = match_reasons

            # Append new match
            matches.append(trade_data_to_save)

            # Write back to file using storage adapter and LOGICAL PATH
            Config.storage.write_json(logical_path, matches)

            trade_number = trade_data_to_save.get('TradeNumber')
            self.logger.info(f"Trade {trade_number} identified and saved to {logical_path} with status: {status}, match_id: {match_id}")

            # Return the match_id for linking with email match
            return match_id

        except Exception as e:
            # --- MODIFICATION: Use log_exception ---
            log_method = getattr(self.logger, 'log_exception', self.logger.log_exception)
            log_method(e, message=f"Failed to save identified trade to {logical_path}")
            # --- End Modification ---
            return None


    def save_email_match(self, trade_data: dict, email_data: dict, match_id=None):
        """Save email match to email_matches.json using logical path."""
        # --- MODIFICATION: Use logical path ---
        file_name = 'email_matches.json'
        logical_path = f"{Config.LOGICAL_ASSET_PREFIX}/{file_name}"
        # --- End Modification ---
        try:
            if match_id is None:
                 self.logger.error("Cannot save email match without a match_id.")
                 return # Or raise error
            match_id = str(match_id) # Ensure string

            # Read existing matches using storage adapter and LOGICAL PATH
            matches = Config.storage.read_json(logical_path)
            if not isinstance(matches, list):
                 self.logger.error(f"Expected list from read_json for {logical_path}, got {type(matches)}. Cannot save email match.")
                 return # Indicate failure

            self.logger.debug(f"Saving email match for match_id: {match_id}")
            # self.logger.debug(f"Trade data for email match: {trade_data}") # Can be verbose
            # self.logger.debug(f"Email data for email match: {email_data}") # Can be verbose

            # Create new match record using only email data
            # Use .get() with defaults for safety
            new_match = {
                "EmailSender": email_data.get("sender_email", "Unknown"),
                "EmailDate": email_data.get("received_date", ""),
                "EmailTime": email_data.get("received_time", ""),
                "EmailSubject": email_data.get("subject", "No Subject"),
                # Use BankTradeNumber from the trade_data derived from the email LLM output
                "BankTradeNumber": str(trade_data.get("BankTradeNumber") or trade_data.get("TradeNumber", "Unknown")),
                "match_id": match_id,  # Add match_id for linking
                "CounterpartyID": trade_data.get("CounterpartyID", ""), # Use data from email trade
                "CounterpartyName": trade_data.get("CounterpartyName", ""),
                "ProductType": trade_data.get("ProductType", ""),
                "Direction": trade_data.get("Direction", ""),
                "Trader": trade_data.get("Trader"), # Keep if needed, default None
                "Currency1": trade_data.get("Currency1", ""),
                "QuantityCurrency1": float(trade_data.get("QuantityCurrency1", 0) or 0),
                "Currency2": trade_data.get("Currency2", ""),
                "SettlementType": trade_data.get("SettlementType", ""),
                "SettlementCurrency": trade_data.get("SettlementCurrency", ""),
                "TradeDate": trade_data.get("TradeDate", ""),
                "ValueDate": trade_data.get("ValueDate", ""),
                "MaturityDate": trade_data.get("MaturityDate", ""),
                "PaymentDate": trade_data.get("PaymentDate", ""),
                "Duration": int(trade_data.get("Duration", 0) or 0),
                "ForwardPrice": float(trade_data.get("ForwardPrice", 0) or 0),
                "FixingReference": trade_data.get("FixingReference", ""),
                "CounterpartyPaymentMethod": trade_data.get("CounterpartyPaymentMethod", ""),
                "OurPaymentMethod": trade_data.get("OurPaymentMethod", ""),
                "EmailBody": email_data.get("body_content", "") # Store email body
            }

            # Append new match
            matches.append(new_match)

            # Write back to file using storage adapter and LOGICAL PATH
            Config.storage.write_json(logical_path, matches)

            bank_trade_number = new_match["BankTradeNumber"]
            self.logger.info(f"Bank trade {bank_trade_number} (match_id: {match_id}) matched with email from {new_match['EmailSender']} and saved to {logical_path}")

        except Exception as e:
            # --- MODIFICATION: Use log_exception ---
            log_method = getattr(self.logger, 'log_exception', self.logger.log_exception)
            log_method(e, message=f"Failed to save email match to {logical_path}")
            # --- End Modification ---
            # Consider re-raising if the caller needs to know


    def is_valid_value(self, value):
        """Check if a value should be considered valid (simple check)."""
        # No changes needed
        if value is None:
            return False
        if isinstance(value, str) and value.strip().upper() in ("", "N/A"): # Check for N/A too
            return False
        # Consider if 0 is a valid value for numeric fields
        # if isinstance(value, (int, float)) and value == 0:
        #     return False
        return True

    async def handle_new_unread_email(self, new_emails: List[Any]): # Use Any for mock email type
        """Process new unread emails, match trades, and save results."""
        # Reload mappings/entities in case they changed since init (optional)
        # self.counterparty_mappings = self.load_counterparty_mappings()
        # self.email_entities = self.load_email_entities()

        # Ensure email_processor and llm_service are available
        if not self.email_processor:
             self.logger.error("EmailProcessorService not available in ConfirmationService.")
             return {"status": "Error", "message": "Internal configuration error (EmailProcessor missing)."}
        if not self.llm_service:
             self.logger.error("LLMService not available in ConfirmationService.")
             return {"status": "Error", "message": "Internal configuration error (LLMService missing)."}


        # Choose your preferred AI provider (Consider making this configurable via Config)
        AI_PROVIDER = "Anthropic"
        #AI_PROVIDER = "OpenAI"
        #AI_PROVIDER = "Google"

        self.logger.info(f"Processing {len(new_emails)} new unread emails using {AI_PROVIDER}")

        # Store results for multiple emails if needed, currently processes one by one
        # For now, return status of the first email processed or first error
        final_result_summary = {}

        for email in new_emails:
            email_id_for_log = getattr(email, 'id', 'N/A')
            self.logger.debug(f"--- Processing Email ID: {email_id_for_log} ---")

            try:
                # --- 1. Extract Email Data ---
                # (Keep existing extraction logic - no changes needed here)
                sender_email = "Unknown"
                if hasattr(email, 'sender') and email.sender and hasattr(email.sender, 'email_address') and email.sender.email_address:
                     raw_email = email.sender.email_address.address
                     if raw_email and '@sandbox.mgsend.net' in raw_email:
                         parts = raw_email.split('=')
                         if len(parts) > 1:
                             username = parts[0]
                             domain_part = parts[1].split('@')[0]
                             sender_email = f"{username}@{domain_part}"
                         else: sender_email = raw_email
                     elif raw_email: sender_email = raw_email

                subject = getattr(email, 'subject', 'No subject')
                received_dt = getattr(email, 'received_date_time', None)
                received_date = received_dt.date().isoformat() if received_dt else datetime.now(UTC).date().isoformat()
                received_time = received_dt.time().isoformat() if received_dt else datetime.now(UTC).time().isoformat()

                self.logger.info(f"Processing email from {sender_email} - Subject: {subject}")

                entity_name, entity_display_name, client_id = self.get_entity_info(sender_email, self.email_entities)
                if entity_name: self.logger.info(f"Email sender identified as {entity_display_name} ({entity_name}), Client ID: {client_id}")
                else: self.logger.warning(f"Unregistered email sender: {sender_email}")

                body_content = 'No body content'
                if hasattr(email, 'body') and email.body and hasattr(email.body, 'content') and email.body.content:
                    body_content = clean_html(email.body.content)

                email_data_for_llm = {
                    "subject": subject, "received_date": received_date, "received_time": received_time,
                    "sender_email": sender_email, "entity_name": entity_name, "client_id": client_id,
                    "body_content": body_content, "attachments_text": "Attachment processing simplified"
                }

                # --- 2. Process with LLM ---
                llm_response_str = None
                llm_data = None
                try:
                    self.logger.info(f"Sending email data (ID: {email_id_for_log}) to LLM for processing.")
                    if not hasattr(self.llm_service, 'process_email_data'):
                         raise AttributeError("LLMService instance does not have 'process_email_data' method.")
                    llm_response_str = self.llm_service.process_email_data(email_data_for_llm, ai_provider=AI_PROVIDER)
                    self.logger.debug(f"LLM Raw Response (ID: {email_id_for_log}): {llm_response_str[:500]}...")
                    llm_data = json.loads(llm_response_str)
                    self.logger.info(f"Successfully parsed LLM response for email ID: {email_id_for_log}")

                except json.JSONDecodeError as je:
                    self.logger.error(f"Failed to parse LLM JSON response for email ID {email_id_for_log}: {je}. Response: {llm_response_str}")
                    final_result_summary = {"status": "Error", "message": "LLM response was not valid JSON."}
                    continue
                except Exception as llm_err:
                    # --- MODIFICATION: Use log_exception ---
                    log_method = getattr(self.logger, 'log_exception', self.logger.log_exception)
                    log_method(llm_err, message=f"Error during LLM processing for email ID {email_id_for_log}")
                    # --- End Modification ---
                    final_result_summary = {"status": "Error", "message": f"LLM processing failed: {str(llm_err)}"}
                    continue

                # --- 3. Analyze LLM Response ---
                is_confirmation = llm_data.get("Email", {}).get("Confirmation", "no").lower() == "yes"

                if not is_confirmation:
                    self.logger.info(f"LLM identified email ID {email_id_for_log} as NOT a trade confirmation.")
                    final_result_summary = {
                        "status": "Not Relevant", "message": "Email does not appear to be a trade confirmation.",
                        "is_confirmation": False, "email_data": {"subject": subject, "sender": sender_email}
                    }
                    continue

                # --- 4. Process Confirmed Trades ---
                self.logger.info(f"LLM identified email ID {email_id_for_log} AS a trade confirmation.")
                trades_in_email = llm_data.get("Trades", [])
                if not trades_in_email:
                    self.logger.warning(f"Confirmation email ID {email_id_for_log} identified, but LLM found no trades within it.")
                    final_result_summary = {
                        "status": "Needs Review", "message": "Confirmation email processed, but no specific trades were extracted by LLM.",
                        "is_confirmation": True
                    }
                    continue

                processed_at_least_one_trade = False
                for trade_from_email in trades_in_email:
                    self.logger.debug(f"Processing trade extracted by LLM from email ID {email_id_for_log}: {trade_from_email.get('TradeNumber')}")

                    # --- 5. Match Trade ---
                    if not self.email_processor:
                         self.logger.error("EmailProcessorService missing, cannot match trade.")
                         continue

                    potential_matches = self.get_potential_trade_matches(email_data_for_llm, trade_from_email)

                    if potential_matches:
                        # --- 6. Process Best Match ---
                        best_match = potential_matches[0]
                        matched_trade_details = best_match["trade"]
                        match_score = best_match["score"]
                        match_reasons = best_match["reasons"]
                        trade_number_internal = matched_trade_details.get("TradeNumber")
                        self.logger.info(f"Best match for email trade: Internal Trade {trade_number_internal} (Score: {match_score})")

                        has_differences = False
                        comparison_details = {}
                        for field, email_value in trade_from_email.items():
                            if field in ["Confirmation_OK", "TradeNumber"]: continue
                            internal_value = matched_trade_details.get(field)
                            norm_email_value = self._normalize_value(email_value)
                            norm_internal_value = self._normalize_value(internal_value)
                            if norm_email_value != norm_internal_value:
                                if self.is_valid_value(email_value):
                                     has_differences = True
                                     comparison_details[field] = {"email": email_value, "internal": internal_value}
                                     self.logger.warning(f"Difference found for Trade {trade_number_internal} - Field '{field}': Email='{email_value}' vs Internal='{internal_value}'")

                        status = "Difference" if has_differences else "Confirmation OK"
                        if match_score < 60: # Low confidence threshold
                            status = "Needs Review"
                            self.logger.warning(f"Low confidence match score ({match_score}) for Trade {trade_number_internal}. Status set to Needs Review.")
                        self.logger.info(f"Final status for Trade {trade_number_internal}: {status}")

                        # --- 7. Save Results ---
                        match_id = self.save_identified_trade(
                            matched_trade_details, status=status,
                            match_score=match_score, match_reasons=match_reasons
                        )
                        if match_id:
                            email_match_data = trade_from_email.copy()
                            email_match_data["BankTradeNumber"] = str(trade_from_email.get("TradeNumber", "Unknown"))
                            email_match_data["CounterpartyName"] = entity_display_name or trade_from_email.get("CounterpartyName", "Unknown")
                            self.save_email_match(email_match_data, email_data_for_llm, match_id=match_id)
                            processed_at_least_one_trade = True
                            if not final_result_summary:
                                 #final_result_summary = {"status": status, "message": self._get_status_message(status), "is_confirmation": True}
                                 final_result_summary = {"status": status, "message": "Match found and processed.", "is_confirmation": True}
                        else:
                             self.logger.error(f"Failed to save identified trade {trade_number_internal}, cannot save email match.")
                             if not final_result_summary:
                                 final_result_summary = {"status": "Error", "message": "Failed to save matched trade data."}

                    else: # No potential match found
                        self.logger.warning(f"No matching trade found in system for trade mentioned in email: {trade_from_email.get('TradeNumber')}")
                        unrecognized_trade_data = trade_from_email.copy()
                        unrecognized_trade_data["BankTradeNumber"] = str(trade_from_email.get("TradeNumber", "Unknown"))
                        unrecognized_trade_data["CounterpartyName"] = entity_display_name or trade_from_email.get("CounterpartyName", "Unknown")
                        unrecognized_trade_data["status"] = "Unrecognized"
                        unrecognized_match_id = str(uuid.uuid4())
                        self.save_email_match(unrecognized_trade_data, email_data_for_llm, match_id=unrecognized_match_id)
                        processed_at_least_one_trade = True
                        if not final_result_summary:
                             final_result_summary = {"status": "Unrecognized", "message": "Trade mentioned in email not found in system.", "is_confirmation": True}

                # --- End loop for trades_in_email ---

                if not final_result_summary and processed_at_least_one_trade:
                     final_result_summary = {"status": "Processed", "message": "Confirmation email processed.", "is_confirmation": True}
                elif not final_result_summary:
                     final_result_summary = {"status": "Needs Review", "message": "Confirmation email processed, but trade details require review.", "is_confirmation": True}

            except Exception as e:
                # --- MODIFICATION: Use log_exception ---
                log_method = getattr(self.logger, 'log_exception', self.logger.log_exception)
                log_method(e, message=f"Error processing email ID {email_id_for_log}")
                # --- End Modification ---
                if not final_result_summary:
                     final_result_summary = {"status": "Error", "message": f"Internal error processing email: {str(e)}"}

            self.logger.debug(f"--- Finished Processing Email ID: {email_id_for_log} ---")

        return final_result_summary if final_result_summary else {"status": "Completed", "message": "Batch processed, no specific status determined."}


    def get_potential_trade_matches(self, email_data: Dict, trade_from_email: Dict) -> List[Dict]:
        """Find potential matching trades using improved counterparty matching and scoring."""
        # No changes needed here regarding file paths, uses email_processor in-memory data
        if not self.email_processor:
             self.logger.error("EmailProcessorService not available in get_potential_trade_matches.")
             return []

        all_trades = self.email_processor.get_all_unmatched_trades()
        if not all_trades:
             self.logger.warning("No unmatched trades loaded to compare against.")
             return []

        potential_matches = []
        identified_counterparty, cp_confidence = self.identify_counterparty(email_data)
        self.logger.debug(f"Matching against identified counterparty: {identified_counterparty} (Confidence: {cp_confidence}%)")

        # Extract key data from email trade for matching
        email_trade_date_str = extract_dates(trade_from_email.get("TradeDate"))
        email_value_date_str = extract_dates(trade_from_email.get("ValueDate"))
        email_ccy1 = str(trade_from_email.get("Currency1", "")).upper()
        email_ccy2 = str(trade_from_email.get("Currency2", "")).upper()
        email_qty1 = self._normalize_value(trade_from_email.get("QuantityCurrency1"), 'number', 0.0)

        self.logger.debug(f"Email trade keys for matching: Date='{email_trade_date_str}', Ccy1='{email_ccy1}', Ccy2='{email_ccy2}', Qty1='{email_qty1}'")

        for internal_trade in all_trades:
            score = 0
            reasons = []

            # 1. Counterparty match (Weight: 30)
            internal_cp_name = str(internal_trade.get("CounterpartyName", "")).lower()
            if identified_counterparty and internal_cp_name:
                identified_cp_lower = identified_counterparty.lower()
                if identified_cp_lower == internal_cp_name:
                    score += 30
                    reasons.append(f"CP Exact: '{identified_counterparty}'")
                elif identified_cp_lower in internal_cp_name or internal_cp_name in identified_cp_lower:
                    score += 20 # Partial match score
                    reasons.append(f"CP Partial: '{identified_counterparty}'~'{internal_trade.get('CounterpartyName')}'")

            # 2. Trade date match (Weight: 25)
            internal_trade_date_str = extract_dates(internal_trade.get("TradeDate"))
            if email_trade_date_str and internal_trade_date_str == email_trade_date_str:
                score += 25
                reasons.append(f"TradeDate: {email_trade_date_str}")

            # 3. Currency pair match (Weight: 20)
            internal_ccy1 = str(internal_trade.get("Currency1", "")).upper()
            internal_ccy2 = str(internal_trade.get("Currency2", "")).upper()
            if email_ccy1 and email_ccy2: # Ensure both email currencies are present
                if email_ccy1 == internal_ccy1 and email_ccy2 == internal_ccy2:
                    score += 20
                    reasons.append(f"CcyPair: {email_ccy1}/{email_ccy2}")
                elif email_ccy1 == internal_ccy2 and email_ccy2 == internal_ccy1:
                    score += 15 # Slightly lower score for reversed
                    reasons.append(f"CcyPair Reversed: {email_ccy1}/{email_ccy2}")

            # 4. Amount match (Weight: 15) - Only check Currency1 amount
            if email_qty1 is not None and abs(email_qty1) > 1e-9: # Check against near-zero float
                internal_qty1 = self._normalize_value(internal_trade.get("QuantityCurrency1"), 'number', 0.0)
                if internal_qty1 is not None and abs(internal_qty1) > 1e-9:
                    tolerance = 0.001 # 0.1%
                    # Use relative difference comparison
                    if abs(email_qty1 - internal_qty1) <= tolerance * max(abs(email_qty1), abs(internal_qty1)):
                        score += 15
                        reasons.append(f"Qty1 Exact: {email_qty1:.2f}")
                    elif abs(email_qty1 - internal_qty1) <= 0.01 * max(abs(email_qty1), abs(internal_qty1)): # 1% tolerance
                         score += 10 # Close match score
                         reasons.append(f"Qty1 Close: {email_qty1:.2f}~{internal_qty1:.2f}")


            # Add as potential match if score exceeds a reasonable threshold
            MATCH_THRESHOLD = 40
            if score >= MATCH_THRESHOLD:
                potential_matches.append({
                    "trade": internal_trade,
                    "score": score,
                    "reasons": reasons
                })
                self.logger.debug(f"Potential match found: Internal Trade {internal_trade.get('TradeNumber')}, Score: {score}, Reasons: {reasons}")

        # Sort by score descending
        return sorted(potential_matches, key=lambda x: x["score"], reverse=True)

    def load_counterparty_mappings(self, file_name="counterparty_mappings.json") -> Dict:
        """Load counterparty mappings using storage adapter and logical path."""
        # --- MODIFICATION: Use logical path ---
        logical_path = f"{Config.LOGICAL_ASSET_PREFIX}/{file_name}"
        # --- End Modification ---
        try:
            self.logger.info(f"Loading counterparty mappings from logical path: {logical_path}")

            # Read using storage adapter and LOGICAL PATH
            mappings = Config.storage.read_json(logical_path)
            if not isinstance(mappings, dict):
                 self.logger.error(f"Expected dict from read_json for {logical_path}, got {type(mappings)}. Returning empty dict.")
                 return {}

            self.logger.info(f"Loaded counterparty mappings for {len(mappings.get('clients', {}))} clients.")
            return mappings
        except Exception as e:
             # --- MODIFICATION: Use log_exception ---
            log_method = getattr(self.logger, 'log_exception', self.logger.log_exception)
            log_method(e, message=f"Failed to load counterparty mappings from {logical_path}")
             # --- End Modification ---
            return {} # Return empty dict on error

    def identify_counterparty(self, source: Dict) -> tuple:
        """Identify counterparty using loaded mappings."""
        # Uses self.counterparty_mappings loaded by load_counterparty_mappings
        # No changes needed here regarding file paths
        mappings = self.counterparty_mappings # Use the loaded mappings

        # Get client-specific mappings (using self.my_entity)
        client_id = self.my_entity
        client_mappings = mappings.get("clients", {}).get(client_id, {})
        using_default_mappings = False
        if not client_mappings:
            client_mappings = mappings.get("clients", {}).get("default", {})
            using_default_mappings = True
            # self.logger.debug(f"No specific mappings for entity '{client_id}', using default mappings.")

        # Prepare source text fields for matching
        sender_email = source.get('sender_email', '').lower()
        subject = source.get('subject', '').lower()
        body = source.get('body_content', '').lower()
        text_content = f"{sender_email} {subject} {body}" # Combine relevant text

        # 1. Email address exact match (Highest confidence)
        if sender_email:
            for name, data in client_mappings.items():
                if any(sender_email == email.lower() for email in data.get('email_accounts', [])):
                    return name, 100

        # 2. Email domain match (High confidence)
        if '@' in sender_email:
            domain = sender_email.split('@')[1]
            for name, data in client_mappings.items():
                if any(domain.endswith(d.lower()) for d in data.get('email_domains', [])):
                    return name, 90

        # 3. Keyword/Alias/Name matching in text content (Lower confidence)
        best_match_name = None
        best_match_score = 0

        # Prioritize longer matches first if checking substrings
        sorted_client_mappings = sorted(client_mappings.items(), key=lambda item: len(item[0]), reverse=True)

        for name, data in sorted_client_mappings:
            current_score = 0
            # Check for full name match (case-insensitive)
            if name.lower() in text_content:
                current_score = 85
            else:
                # Check aliases (case-insensitive)
                for alias in sorted(data.get('aliases', []), key=len, reverse=True): # Check longer aliases first
                    if alias.lower() in text_content:
                        current_score = 80
                        break # Found best alias match for this counterparty

            if current_score > best_match_score:
                best_match_score = current_score
                best_match_name = name
                # Optimization: If we get a high score (e.g., full name match), maybe stop early?
                # if best_match_score == 85: break

        if best_match_name:
            return best_match_name, best_match_score

        # No match found
        return None, 0

    # --- Helper method for normalization ---
    def _normalize_value(self, value: Any, target_type: str = 'string', default: Any = None) -> Any:
        """Normalizes value for comparison or storage."""
        # No changes needed here
        if value is None or pd.isna(value):
            return default

        if isinstance(value, str):
            value = value.strip()
            if value.upper() == 'N/A':
                return default

        if target_type == 'string':
            return str(value)
        elif target_type == 'number':
            try:
                # Handle strings with commas
                if isinstance(value, str):
                     value = value.replace(',', '')
                return float(value)
            except (ValueError, TypeError):
                # Return default if conversion fails
                return float(default) if default is not None else None
        elif target_type == 'date':
             # Try to format consistently if it's a date object
             if isinstance(value, (datetime, pd.Timestamp)):
                 return value.strftime('%d-%m-%Y')
             elif isinstance(value, str):
                 # Optional: Add more robust date parsing/validation here if needed
                 return value # Assume string is already in correct format for now
             else:
                 # Return default if not a recognizable date type
                 return str(default) if default is not None else None
        else:
            return value