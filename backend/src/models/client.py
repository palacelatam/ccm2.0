"""
Client models matching Firestore schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base import BaseFirestoreModel, UserReference


# Client Settings Models
class AutoConfirmSettings(BaseModel):
    """Auto-confirmation settings"""
    enabled: bool = False
    delay_minutes: int = Field(0, alias="delayMinutes")
    
    class Config:
        populate_by_name = True


class AutomationSettings(BaseModel):
    """Automation configuration settings"""
    data_sharing: bool = Field(False, alias="dataSharing")
    auto_confirm_matched: AutoConfirmSettings = Field(default_factory=AutoConfirmSettings, alias="autoConfirmMatched")
    auto_carta_instruccion: bool = Field(False, alias="autoCartaInstruccion")
    auto_confirm_disputed: AutoConfirmSettings = Field(default_factory=AutoConfirmSettings, alias="autoConfirmDisputed")
    
    class Config:
        populate_by_name = True


class EmailAlertSettings(BaseModel):
    """Email alert configuration"""
    enabled: bool = False
    emails: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


class WhatsappAlertSettings(BaseModel):
    """WhatsApp alert configuration"""
    enabled: bool = False
    phones: List[str] = Field(default_factory=list)
    
    class Config:
        populate_by_name = True


class AlertSettings(BaseModel):
    """Alert configuration settings"""
    email_confirmed_trades: EmailAlertSettings = Field(default_factory=EmailAlertSettings, alias="emailConfirmedTrades")
    email_disputed_trades: EmailAlertSettings = Field(default_factory=EmailAlertSettings, alias="emailDisputedTrades")
    whatsapp_confirmed_trades: WhatsappAlertSettings = Field(default_factory=WhatsappAlertSettings, alias="whatsappConfirmedTrades")
    whatsapp_disputed_trades: WhatsappAlertSettings = Field(default_factory=WhatsappAlertSettings, alias="whatsappDisputedTrades")
    
    class Config:
        populate_by_name = True


class PreferencesSettings(BaseModel):
    """System preferences"""
    language: str = "es"
    timezone: str = "America/Santiago"
    date_format: str = Field("DD/MM/YYYY", alias="dateFormat")
    number_format: str = Field("1.234,56", alias="numberFormat")
    
    class Config:
        populate_by_name = True


class ClientSettings(BaseFirestoreModel):
    """Client settings configuration document"""
    automation: AutomationSettings = Field(default_factory=AutomationSettings)
    alerts: AlertSettings = Field(default_factory=AlertSettings)
    preferences: PreferencesSettings = Field(default_factory=PreferencesSettings)


class ClientSettingsUpdate(BaseModel):
    """Model for updating client settings"""
    automation: Optional[AutomationSettings] = None
    alerts: Optional[AlertSettings] = None
    preferences: Optional[PreferencesSettings] = None


# Bank Account Models
class BankAccount(BaseFirestoreModel):
    """Bank account model"""
    active: bool = True
    account_name: str = Field(alias="accountName")
    bank_name: str = Field(alias="bankName")
    swift_code: str = Field(alias="swiftCode")
    account_currency: str = Field(alias="accountCurrency")
    account_number: str = Field(alias="accountNumber")  # Should be encrypted
    is_default: bool = Field(False, alias="isDefault")
    
    class Config:
        populate_by_name = True


class BankAccountCreate(BaseModel):
    """Model for creating a bank account"""
    account_name: str = Field(alias="accountName")
    bank_name: str = Field(alias="bankName")
    swift_code: str = Field(alias="swiftCode")
    account_currency: str = Field(alias="accountCurrency")
    account_number: str = Field(alias="accountNumber")
    is_default: bool = Field(False, alias="isDefault")
    
    class Config:
        populate_by_name = True


class BankAccountUpdate(BaseModel):
    """Model for updating a bank account"""
    active: Optional[bool] = None
    account_name: Optional[str] = Field(None, alias="accountName")
    bank_name: Optional[str] = Field(None, alias="bankName")
    swift_code: Optional[str] = Field(None, alias="swiftCode")
    account_currency: Optional[str] = Field(None, alias="accountCurrency")
    account_number: Optional[str] = Field(None, alias="accountNumber")
    is_default: Optional[bool] = Field(None, alias="isDefault")
    
    class Config:
        populate_by_name = True


# Settlement Rules Models
class SettlementRule(BaseFirestoreModel):
    """Settlement rule model"""
    active: bool = True
    priority: int = 1
    name: str
    counterparty: str
    cashflow_currency: str = Field(alias="cashflowCurrency")
    direction: str  # IN, OUT
    product: str  # FX_SPOT, FX_FORWARD, FX_SWAP
    bank_account_id: str = Field(alias="bankAccountId")  # Reference to bank account
    
    class Config:
        populate_by_name = True


class SettlementRuleCreate(BaseModel):
    """Model for creating a settlement rule"""
    name: str
    counterparty: str
    cashflow_currency: str = Field(alias="cashflowCurrency")
    direction: str
    product: str
    bank_account_id: str = Field(alias="bankAccountId")
    priority: int = 1
    
    class Config:
        populate_by_name = True


class SettlementRuleUpdate(BaseModel):
    """Model for updating a settlement rule"""
    active: Optional[bool] = None
    priority: Optional[int] = None
    name: Optional[str] = None
    counterparty: Optional[str] = None
    cashflow_currency: Optional[str] = Field(None, alias="cashflowCurrency")
    direction: Optional[str] = None
    product: Optional[str] = None
    bank_account_id: Optional[str] = Field(None, alias="bankAccountId")
    
    class Config:
        populate_by_name = True


# Data Mapping Models
class TransformationParams(BaseModel):
    """Transformation parameters"""
    # This will vary based on transformation type
    # Using flexible dict for now
    params: Dict[str, Any] = Field(default_factory=dict)


class FieldTransformation(BaseModel):
    """Field transformation rules"""
    type: str  # direct, format, enum, split, combine
    params: Dict[str, Any] = Field(default_factory=dict)


class FieldMapping(BaseModel):
    """Field mapping configuration"""
    source_field: str = Field(alias="sourceField")
    target_field: str = Field(alias="targetField")
    transformation: FieldTransformation
    
    class Config:
        populate_by_name = True


class ExpectedField(BaseModel):
    """Expected field definition"""
    name: str
    type: str
    required: bool = False
    format: Optional[str] = None
    enum_values: Optional[List[str]] = Field(None, alias="enumValues")
    
    class Config:
        populate_by_name = True


class DataMapping(BaseFirestoreModel):
    """Data mapping configuration"""
    name: str
    description: str
    file_type: str = Field(alias="fileType")  # csv, excel, json
    is_default: bool = Field(False, alias="isDefault")
    field_mappings: List[FieldMapping] = Field(default_factory=list, alias="fieldMappings")
    expected_fields: List[ExpectedField] = Field(default_factory=list, alias="expectedFields")
    last_used_at: Optional[datetime] = Field(None, alias="lastUsedAt")
    usage_count: int = Field(0, alias="usageCount")
    
    class Config:
        populate_by_name = True


class DataMappingCreate(BaseModel):
    """Model for creating a data mapping"""
    name: str
    description: str
    file_type: str = Field(alias="fileType")
    is_default: bool = Field(False, alias="isDefault")
    field_mappings: List[FieldMapping] = Field(default_factory=list, alias="fieldMappings")
    expected_fields: List[ExpectedField] = Field(default_factory=list, alias="expectedFields")
    
    class Config:
        populate_by_name = True


class DataMappingUpdate(BaseModel):
    """Model for updating a data mapping"""
    name: Optional[str] = None
    description: Optional[str] = None
    file_type: Optional[str] = Field(None, alias="fileType")
    is_default: Optional[bool] = Field(None, alias="isDefault")
    field_mappings: Optional[List[FieldMapping]] = Field(None, alias="fieldMappings")
    expected_fields: Optional[List[ExpectedField]] = Field(None, alias="expectedFields")
    
    class Config:
        populate_by_name = True


# Client User Override Models  
class ClientUserOverride(BaseFirestoreModel):
    """Client-specific user settings and overrides"""
    user_id: str = Field(alias="userId")  # Reference to main user document
    client_specific_role: Optional[str] = Field(None, alias="clientSpecificRole")  # Reference to role
    permissions: List[str] = Field(default_factory=list)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    last_access_at: Optional[datetime] = Field(None, alias="lastAccessAt")
    is_active: bool = Field(True, alias="isActive")
    
    class Config:
        populate_by_name = True