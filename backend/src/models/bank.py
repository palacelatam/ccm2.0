"""
Bank models matching Firestore schema
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .base import BaseFirestoreModel, UserReference


# Bank Root Model
class Bank(BaseFirestoreModel):
    """Bank root document model"""
    name: str = Field(..., description="Bank name")
    tax_id: str = Field(..., description="Tax identification number")
    country: str = Field("CL", description="Country code")
    swift_code: Optional[str] = Field(None, description="Bank's SWIFT/BIC code")
    status: str = Field("active", description="Bank status")


class BankCreate(BaseModel):
    """Bank creation model"""
    name: str
    tax_id: str
    country: str = "CL"
    swift_code: Optional[str] = None
    status: str = "active"


class BankUpdate(BaseModel):
    """Bank update model"""
    name: Optional[str] = None
    tax_id: Optional[str] = None
    country: Optional[str] = None
    swift_code: Optional[str] = None
    status: Optional[str] = None


# Client Segmentation Models
class ClientSegment(BaseFirestoreModel):
    """Client segment model"""
    name: str = Field(..., description="Segment name")
    description: str = Field("", description="Segment description")
    color: Optional[str] = Field("#007bff", description="Segment color for UI")


class ClientSegmentCreate(BaseModel):
    """Client segment creation model"""
    name: str
    description: str = ""
    color: str = "#007bff"


class ClientSegmentUpdate(BaseModel):
    """Client segment update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None


# Settlement Instruction Letters Models
class SettlementInstructionLetter(BaseFirestoreModel):
    """Settlement instruction letter template model"""
    active: bool = Field(True, description="Whether the template is active")
    priority: int = Field(0, description="Priority order for template selection")
    rule_name: str = Field(..., description="Template rule name")
    product: str = Field(..., description="Financial product type")
    settlement_type: str = Field(..., description="Settlement type (Compensación or Entrega Física)")
    client_segment_id: Optional[str] = Field(None, description="Associated client segment ID")
    document_name: Optional[str] = Field(None, description="Original document filename")
    document_url: Optional[str] = Field(None, description="Cloud storage URL for the document")
    document_storage_path: Optional[str] = Field(None, description="Cloud storage path for generating signed URLs")
    document_size: Optional[int] = Field(None, description="Document file size in bytes")
    document_content_type: Optional[str] = Field(None, description="Document MIME content type")
    document_uploaded_at: Optional[str] = Field(None, description="Document upload timestamp")
    template_variables: List[str] = Field(default_factory=list, description="Available template variables")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Template selection conditions")


class SettlementInstructionLetterCreate(BaseModel):
    """Settlement instruction letter creation model"""
    active: bool = True
    priority: int = 0
    rule_name: str
    product: str
    settlement_type: str
    client_segment_id: Optional[str] = None
    document_name: Optional[str] = None
    document_url: Optional[str] = None
    template_variables: List[str] = Field(default_factory=list)
    conditions: Dict[str, Any] = Field(default_factory=dict)


class SettlementInstructionLetterUpdate(BaseModel):
    """Settlement instruction letter update model"""
    active: Optional[bool] = None
    priority: Optional[int] = None
    rule_name: Optional[str] = None
    product: Optional[str] = None
    settlement_type: Optional[str] = None
    client_segment_id: Optional[str] = None
    document_name: Optional[str] = None
    document_url: Optional[str] = None
    document_storage_path: Optional[str] = None
    document_size: Optional[int] = None
    document_content_type: Optional[str] = None
    document_uploaded_at: Optional[str] = None
    template_variables: Optional[List[str]] = None
    conditions: Optional[Dict[str, Any]] = None


# Bank System Settings Model
class BankSystemSettings(BaseFirestoreModel):
    """Bank system settings model"""
    default_currency: str = Field("USD", description="Bank's default currency")
    supported_currencies: List[str] = Field(default_factory=lambda: ["USD", "EUR", "CLP"], description="Supported currencies")
    supported_products: List[str] = Field(
        default_factory=lambda: ["FX_SPOT", "FX_FORWARD", "FX_SWAP", "NDF", "OPTION"],
        description="Supported financial products"
    )


class BankSystemSettingsUpdate(BaseModel):
    """Bank system settings update model"""
    default_currency: Optional[str] = None
    supported_currencies: Optional[List[str]] = None
    supported_products: Optional[List[str]] = None


# Client-Segment Assignment Model
class ClientSegmentAssignment(BaseModel):
    """Model for assigning clients to segments"""
    client_id: str = Field(..., description="Client ID to assign")
    segment_id: str = Field(..., description="Segment ID to assign to")


class BulkClientSegmentAssignment(BaseModel):
    """Model for bulk client-segment assignments"""
    assignments: List[ClientSegmentAssignment] = Field(..., description="List of client-segment assignments")


# Document Upload Model for Settlement Letters
class DocumentUpload(BaseModel):
    """Model for document upload metadata"""
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME type")
    size: int = Field(..., description="File size in bytes")
    upload_url: Optional[str] = Field(None, description="Temporary upload URL")


# Template Variable Model
class TemplateVariable(BaseModel):
    """Model for template variables in settlement letters"""
    name: str = Field(..., description="Variable name")
    type: str = Field(..., description="Variable type (text, date, number, etc.)")
    description: str = Field("", description="Variable description")
    required: bool = Field(True, description="Whether variable is required")


# Comprehensive Template Model with Variables
class SettlementTemplate(BaseModel):
    """Comprehensive settlement template model with variables"""
    template: SettlementInstructionLetter
    variables: List[TemplateVariable] = Field(default_factory=list)
    preview_data: Optional[Dict[str, Any]] = Field(None, description="Sample data for template preview")