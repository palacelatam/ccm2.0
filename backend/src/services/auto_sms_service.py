"""
Automated SMS Service for generating and sending trade notification SMS messages
"""
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from services.sms_service import sms_service
from config.firebase_config import get_cmek_firestore_client

logger = logging.getLogger(__name__)


class AutoSmsService:
    """Service for automated SMS notifications based on trade events"""
    
    def __init__(self):
        """Initialize the auto SMS service"""
        self.sms_service = sms_service
        logger.info("AutoSmsService initialized")
    
    async def process_trade_sms_notifications(
        self,
        client_id: str,
        trade_status: str,
        trade_data: Dict[str, Any],
        discrepancies: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Process SMS notifications for a trade based on client configuration
        
        Args:
            client_id: Client ID
            trade_status: Trade status (Confirmation OK, Difference, Needs Review)
            trade_data: Trade information
            discrepancies: List of field discrepancies (for disputed trades)
            
        Returns:
            Dict containing SMS sending results
        """
        results = {
            'client_id': client_id,
            'trade_number': trade_data.get('TradeNumber', 'Unknown'),
            'sms_sent': False,
            'confirmed_sms': None,
            'disputed_sms': None,
            'errors': []
        }
        
        try:
            # Get client SMS configuration
            db = get_cmek_firestore_client()
            config_ref = db.collection('clients').document(client_id).collection('settings').document('configuration')
            config_doc = config_ref.get()
            
            if not config_doc.exists:
                logger.warning(f"No configuration found for client {client_id}")
                results['errors'].append("Client configuration not found")
                return results
            
            config_data = config_doc.to_dict()
            alerts = config_data.get('alerts', {})
            
            # Get client info for organization name
            client_ref = db.collection('clients').document(client_id)
            client_doc = client_ref.get()
            
            if not client_doc.exists:
                logger.error(f"Client document {client_id} not found")
                results['errors'].append("Client not found")
                return results
            
            client_data = client_doc.to_dict()
            organization_name = client_data.get('name', client_data.get('organizationName', 'Organization'))
            language = client_data.get('preferences', {}).get('language', 'es')
            
            # Process based on trade status
            if trade_status == "Confirmation OK":
                # Check if confirmed trade SMS is enabled
                sms_config = alerts.get('smsConfirmedTrades', {})
                if sms_config.get('enabled') and sms_config.get('phones'):
                    logger.info(f"Sending confirmed trade SMS for client {client_id}")
                    
                    # Generate SMS content
                    sms_content = await self._generate_confirmed_trade_sms(
                        trade_data=trade_data,
                        organization_name=organization_name,
                        language=language
                    )
                    
                    # Send SMS to all configured phones
                    sms_results = await self.sms_service.send_bulk_sms(
                        phone_list=sms_config['phones'],
                        message=sms_content,
                        client_id=client_id,
                        trade_number=trade_data.get('TradeNumber')
                    )
                    
                    results['confirmed_sms'] = sms_results
                    results['sms_sent'] = any(r.get('success') for r in sms_results)
                    
            elif trade_status in ["Difference", "Needs Review"]:
                # Check if disputed trade SMS is enabled
                sms_config = alerts.get('smsDisputedTrades', {})
                if sms_config.get('enabled') and sms_config.get('phones'):
                    logger.info(f"Sending disputed trade SMS for client {client_id}")
                    
                    # Generate SMS content
                    sms_content = await self._generate_disputed_trade_sms(
                        trade_data=trade_data,
                        discrepancies=discrepancies or [],
                        organization_name=organization_name,
                        language=language
                    )
                    
                    # Send SMS to all configured phones
                    sms_results = await self.sms_service.send_bulk_sms(
                        phone_list=sms_config['phones'],
                        message=sms_content,
                        client_id=client_id,
                        trade_number=trade_data.get('TradeNumber')
                    )
                    
                    results['disputed_sms'] = sms_results
                    results['sms_sent'] = any(r.get('success') for r in sms_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Error processing SMS notifications: {e}")
            results['errors'].append(str(e))
            return results
    
    async def _generate_confirmed_trade_sms(
        self,
        trade_data: Dict[str, Any],
        organization_name: str,
        language: str = 'es'
    ) -> str:
        """
        Generate SMS content for confirmed trades
        
        Args:
            trade_data: Trade information
            organization_name: Client organization name
            language: Language code (es, en, pt)
            
        Returns:
            SMS message content (max 160 chars)
        """
        trade_number = trade_data.get('TradeNumber', 'Unknown')
        counterparty = trade_data.get('CounterpartyName', 'Unknown')
        amount = trade_data.get('QuantityCurrency1', 0)
        currency = trade_data.get('Currency1', 'USD')
        
        # Format amount
        if isinstance(amount, (int, float)):
            amount_str = f"{amount:,.0f}"
        else:
            amount_str = str(amount)
        
        # Generate message based on language
        if language == 'es':
            message = (
                f"✅ Trade #{trade_number} confirmado\n"
                f"Contraparte: {counterparty}\n"
                f"Monto: {amount_str} {currency}\n"
                f"Estado: CONFIRMADO\n"
                f"- {organization_name}"
            )
        elif language == 'pt':
            message = (
                f"✅ Trade #{trade_number} confirmado\n"
                f"Contraparte: {counterparty}\n"
                f"Valor: {amount_str} {currency}\n"
                f"Status: CONFIRMADO\n"
                f"- {organization_name}"
            )
        else:  # English
            message = (
                f"✅ Trade #{trade_number} confirmed\n"
                f"Counterparty: {counterparty}\n"
                f"Amount: {amount_str} {currency}\n"
                f"Status: CONFIRMED\n"
                f"- {organization_name}"
            )
        
        # Ensure message fits in 160 characters
        if len(message) > 160:
            # Shorten counterparty name if needed
            max_cp_length = 160 - len(message) + len(counterparty)
            if max_cp_length < len(counterparty):
                counterparty_short = counterparty[:max_cp_length-3] + "..."
                message = message.replace(counterparty, counterparty_short)
        
        return message
    
    async def _generate_disputed_trade_sms(
        self,
        trade_data: Dict[str, Any],
        discrepancies: List[Dict],
        organization_name: str,
        language: str = 'es'
    ) -> str:
        """
        Generate SMS content for disputed trades
        
        Args:
            trade_data: Trade information
            discrepancies: List of field discrepancies
            organization_name: Client organization name
            language: Language code (es, en, pt)
            
        Returns:
            SMS message content (max 160 chars)
        """
        trade_number = trade_data.get('TradeNumber', 'Unknown')
        counterparty = trade_data.get('CounterpartyName', 'Unknown')
        discrepancy_count = len(discrepancies) if discrepancies else 0
        
        # Generate message based on language
        if language == 'es':
            message = (
                f"⚠️ Trade #{trade_number} con discrepancias\n"
                f"Contraparte: {counterparty}\n"
                f"Revisar: {discrepancy_count} campos\n"
                f"Acción requerida\n"
                f"- {organization_name}"
            )
        elif language == 'pt':
            message = (
                f"⚠️ Trade #{trade_number} com discrepâncias\n"
                f"Contraparte: {counterparty}\n"
                f"Revisar: {discrepancy_count} campos\n"
                f"Ação necessária\n"
                f"- {organization_name}"
            )
        else:  # English
            message = (
                f"⚠️ Trade #{trade_number} disputed\n"
                f"Counterparty: {counterparty}\n"
                f"Review: {discrepancy_count} fields\n"
                f"Action required\n"
                f"- {organization_name}"
            )
        
        # Ensure message fits in 160 characters
        if len(message) > 160:
            # Shorten counterparty name if needed
            max_cp_length = 160 - len(message) + len(counterparty)
            if max_cp_length < len(counterparty):
                counterparty_short = counterparty[:max_cp_length-3] + "..."
                message = message.replace(counterparty, counterparty_short)
        
        return message
    
    async def send_test_sms(
        self,
        phone_number: str,
        client_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a test SMS message
        
        Args:
            phone_number: Recipient phone number
            client_id: Optional client ID
            
        Returns:
            SMS sending result
        """
        test_message = (
            "🔔 Test SMS from CCM2.0\n"
            "This is a test message to verify SMS delivery.\n"
            "If you receive this, SMS is working correctly!"
        )
        
        result = await self.sms_service.send_sms(
            to_phone=phone_number,
            message=test_message,
            client_id=client_id
        )
        
        logger.info(f"Test SMS sent to {phone_number}: {result.get('success')}")
        return result


# Global instance
auto_sms_service = AutoSmsService()