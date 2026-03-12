from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, Boolean, Float, Interval, JSON, ARRAY, TIMESTAMP, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.db.database import Base

# Use JSON for SQLite compatibility, JSONB for PostgreSQL
# SQLAlchemy will auto-detect based on database

class ChannelType(str, enum.Enum):
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    WEB_FORM = "web_form"

class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"

class MessagePriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class SentimentType(str, enum.Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    customer_type = Column(String, default="individual")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    custom_metadata = Column(JSON, default=dict, name="metadata")
    
    tickets = relationship("Ticket", back_populates="customer")
    identifiers = relationship("CustomerIdentifier", back_populates="customer")

class CustomerIdentifier(Base):
    __tablename__ = "customer_identifiers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"))
    channel = Column(Enum(ChannelType), nullable=False)
    identifier = Column(String, nullable=False)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="identifiers")
    __table_args__ = (
        UniqueConstraint('customer_id', 'channel', 'identifier', name='uq_customer_channel_identifier'),
    )

from sqlalchemy.schema import UniqueConstraint

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String(100))
    tags = Column(String(500))  # Comma-separated for SQLite compatibility
    # embedding = Column(Vector(384))  # pgvector - enabled in production
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    usage_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"))
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    channel = Column(Enum(ChannelType), nullable=False)
    subject = Column(String(500))
    priority = Column(Enum(MessagePriority), default=MessagePriority.MEDIUM)
    sentiment = Column(Enum(SentimentType), default=SentimentType.NEUTRAL)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to_human = Column(Boolean, default=False)
    assigned_to_agent = Column(Integer, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    first_response_time = Column(Interval, nullable=True)
    resolution_time = Column(Interval, nullable=True)
    custom_metadata = Column(JSON, default=dict, name="metadata")
    
    customer = relationship("Customer", back_populates="tickets")
    messages = relationship("Message", back_populates="ticket", order_by="Message.created_at")
    conversations = relationship("Conversation", back_populates="ticket")
    escalations = relationship("EscalationLog", back_populates="ticket")

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"))
    session_id = Column(String(255), unique=True)
    status = Column(String(50), default="active")
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    message_count = Column(Integer, default=0)
    last_message_at = Column(DateTime, nullable=True)
    context_summary = Column(Text, nullable=True)
    custom_metadata = Column(JSON, default=dict, name="metadata")
    
    ticket = relationship("Ticket", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"))
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    content = Column(Text, nullable=False)
    content_html = Column(Text, nullable=True)
    is_from_customer = Column(Boolean, default=True)
    channel = Column(Enum(ChannelType), nullable=False)
    message_type = Column(String(50), default="text")
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)
    ai_confidence = Column(Float, nullable=True)
    sentiment = Column(Enum(SentimentType), default=SentimentType.NEUTRAL)
    sentiment_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    custom_metadata = Column(JSON, default=dict, name="metadata")
    
    ticket = relationship("Ticket", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")

class ChannelConfig(Base):
    __tablename__ = "channel_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    channel = Column(Enum(ChannelType), unique=True, nullable=False)
    enabled = Column(Boolean, default=True)
    config = Column(JSON, default=dict)
    rate_limit = Column(Integer, default=100)
    rate_limit_period = Column(Integer, default=60)
    auto_response_enabled = Column(Boolean, default=True)
    escalation_keywords = Column(String(500))  # Comma-separated for SQLite
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentMetric(Base):
    __tablename__ = "agent_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    channel = Column(Enum(ChannelType), nullable=True)
    total_messages = Column(Integer, default=0)
    ai_handled = Column(Integer, default=0)
    human_escalated = Column(Integer, default=0)
    avg_response_time_ms = Column(Integer, default=0)
    avg_resolution_time_min = Column(Integer, default=0)
    customer_satisfaction = Column(Float, nullable=True)
    accuracy_rate = Column(Float, nullable=True)
    escalation_rate = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class EscalationLog(Base):
    __tablename__ = "escalation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"))
    reason = Column(String(255), nullable=False)
    escalated_by = Column(String(100), default="ai")
    escalated_to = Column(Integer, nullable=True)
    priority = Column(Enum(MessagePriority))
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    ticket = relationship("Ticket", back_populates="escalations")
