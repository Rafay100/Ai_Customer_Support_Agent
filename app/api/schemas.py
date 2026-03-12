from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum

class ChannelType(str, Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

# Request Schemas
class MessageCreate(BaseModel):
    content: str
    channel: ChannelType
    customer_email: Optional[EmailStr] = None
    customer_phone: Optional[str] = None
    customer_name: Optional[str] = None
    subject: Optional[str] = None

class WebFormMessage(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

class WhatsAppMessage(BaseModel):
    from_number: str
    content: str

class EmailMessage(BaseModel):
    from_email: str
    subject: str
    content: str
    in_reply_to: Optional[str] = None

# Response Schemas
class MessageResponse(BaseModel):
    id: int
    ticket_id: int
    content: str
    is_from_customer: bool
    channel: ChannelType
    created_at: datetime
    ai_generated: bool
    
    class Config:
        from_attributes = True

class TicketResponse(BaseModel):
    id: int
    customer_id: int
    status: TicketStatus
    channel: ChannelType
    subject: Optional[str]
    created_at: datetime
    assigned_to_human: bool
    
    class Config:
        from_attributes = True

class AIResponse(BaseModel):
    response: str
    should_escalate: bool
    confidence: str

class SupportResponse(BaseModel):
    ticket_id: int
    ai_response: Optional[str]
    escalated: bool
    message: str
