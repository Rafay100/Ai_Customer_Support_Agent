"""
MCP-style Tools for AI Agent
These tools can be called by the AI agent or exposed via MCP server
"""
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
import json

class MCPTools:
    """
    Model Context Protocol (MCP) style tools
    Can be used by AI agents or exposed via API
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def search_knowledge_base(
        self, 
        query: str, 
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """
        Search knowledge base for relevant articles
        
        Args:
            query: Search query
            limit: Maximum results to return
            category: Optional category filter
        
        Returns:
            List of matching knowledge base articles
        """
        from app.models.models import KnowledgeBase
        
        query_obj = self.db.query(KnowledgeBase).filter(
            KnowledgeBase.is_active == True
        )
        
        if category:
            query_obj = query_obj.filter(KnowledgeBase.category == category)
        
        # Simple keyword search (enhance with semantic search in production)
        keywords = query.lower().split()
        results = []
        
        for kb in query_obj.all():
            score = 0
            text = f"{kb.question} {kb.answer}".lower()
            for keyword in keywords:
                if keyword in text:
                    score += 1
            
            if score > 0:
                results.append({
                    "id": kb.id,
                    "question": kb.question,
                    "answer": kb.answer,
                    "category": kb.category,
                    "tags": kb.tags,
                    "score": score
                })
        
        # Sort by score and limit
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:limit]
    
    def create_ticket(
        self,
        customer_id: int,
        channel: str,
        subject: str,
        content: str,
        priority: str = "medium"
    ) -> Dict:
        """
        Create a new support ticket
        
        Args:
            customer_id: Customer ID
            channel: Channel (email, whatsapp, web_form)
            subject: Ticket subject
            content: Message content
            priority: Priority level
        
        Returns:
            Created ticket information
        """
        from app.models.models import Ticket, Message, ChannelType, TicketStatus, MessagePriority
        
        # Map channel string to enum
        channel_map = {
            "email": ChannelType.EMAIL,
            "whatsapp": ChannelType.WHATSAPP,
            "web_form": ChannelType.WEB_FORM
        }
        
        ticket = Ticket(
            customer_id=customer_id,
            channel=channel_map.get(channel, ChannelType.WEB_FORM),
            subject=subject,
            priority=MessagePriority(priority),
            status=TicketStatus.OPEN
        )
        
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        
        # Add initial message
        message = Message(
            ticket_id=ticket.id,
            content=content,
            is_from_customer=True,
            channel=channel_map.get(channel, ChannelType.WEB_FORM)
        )
        self.db.add(message)
        self.db.commit()
        
        return {
            "ticket_id": ticket.id,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "created_at": ticket.created_at.isoformat()
        }
    
    def get_customer_history(
        self,
        customer_id: int,
        limit: int = 10
    ) -> Dict:
        """
        Get customer's ticket history
        
        Args:
            customer_id: Customer ID
            limit: Maximum tickets to return
        
        Returns:
            Customer information and ticket history
        """
        from app.models.models import Customer, Ticket
        
        customer = self.db.query(Customer).filter(
            Customer.id == customer_id
        ).first()
        
        if not customer:
            return {"error": "Customer not found"}
        
        tickets = self.db.query(Ticket).filter(
            Ticket.customer_id == customer_id
        ).order_by(Ticket.created_at.desc()).limit(limit).all()
        
        return {
            "customer": {
                "id": customer.id,
                "name": customer.name,
                "email": customer.email,
                "phone": customer.phone,
                "created_at": customer.created_at.isoformat()
            },
            "tickets": [
                {
                    "id": t.id,
                    "subject": t.subject,
                    "status": t.status.value,
                    "channel": t.channel.value,
                    "created_at": t.created_at.isoformat()
                }
                for t in tickets
            ],
            "total_tickets": len(tickets)
        }
    
    def escalate_to_human(
        self,
        ticket_id: int,
        reason: str,
        priority: str = "high",
        notes: Optional[str] = None
    ) -> Dict:
        """
        Escalate ticket to human agent
        
        Args:
            ticket_id: Ticket ID to escalate
            reason: Reason for escalation
            priority: Priority level
            notes: Additional notes
        
        Returns:
            Escalation information
        """
        from app.models.models import Ticket, TicketStatus, EscalationLog, MessagePriority
        
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            return {"error": "Ticket not found"}
        
        # Update ticket
        ticket.status = TicketStatus.ESCALATED
        ticket.assigned_to_human = True
        ticket.priority = MessagePriority(priority)
        
        # Create escalation log
        escalation = EscalationLog(
            ticket_id=ticket_id,
            reason=reason,
            priority=MessagePriority(priority),
            notes=notes
        )
        self.db.add(escalation)
        self.db.commit()
        
        # Add internal message
        internal_message = Message(
            ticket_id=ticket_id,
            content=f"[ESCALATION] Ticket escalated to human agent. Reason: {reason}",
            is_from_customer=False,
            channel=ticket.channel,
            ai_generated=False
        )
        self.db.add(internal_message)
        self.db.commit()
        
        return {
            "ticket_id": ticket_id,
            "escalated": True,
            "reason": reason,
            "priority": priority,
            "escalation_id": escalation.id
        }
    
    def send_response(
        self,
        ticket_id: int,
        content: str,
        channel: str,
        ai_generated: bool = True
    ) -> Dict:
        """
        Send response to customer
        
        Args:
            ticket_id: Ticket ID
            content: Response content
            channel: Channel to send via
            ai_generated: Whether response is AI-generated
        
        Returns:
            Message information
        """
        from app.models.models import Message, Ticket, ChannelType
        
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            return {"error": "Ticket not found"}
        
        # Map channel
        channel_map = {
            "email": ChannelType.EMAIL,
            "whatsapp": ChannelType.WHATSAPP,
            "web_form": ChannelType.WEB_FORM
        }
        
        message = Message(
            ticket_id=ticket_id,
            content=content,
            is_from_customer=False,
            channel=channel_map.get(channel, ticket.channel),
            ai_generated=ai_generated
        )
        
        self.db.add(message)
        
        # Update ticket status
        if ticket.status == TicketStatus.OPEN:
            ticket.status = TicketStatus.IN_PROGRESS
        
        self.db.commit()
        
        return {
            "message_id": message.id,
            "ticket_id": ticket_id,
            "sent": True,
            "timestamp": message.created_at.isoformat()
        }
    
    def get_ticket_status(self, ticket_id: int) -> Dict:
        """Get ticket status and details"""
        from app.models.models import Ticket
        
        ticket = self.db.query(Ticket).filter(Ticket.id == ticket_id).first()
        
        if not ticket:
            return {"error": "Ticket not found"}
        
        return {
            "ticket_id": ticket.id,
            "status": ticket.status.value,
            "priority": ticket.priority.value,
            "channel": ticket.channel.value,
            "assigned_to_human": ticket.assigned_to_human,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat()
        }
    
    def analyze_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of text"""
        from app.services.routing_rules import simple_sentiment_analysis
        
        sentiment = simple_sentiment_analysis(text)
        
        return {
            "sentiment": sentiment,
            "text": text[:100] + "..." if len(text) > 100 else text
        }


# Tool definitions for OpenAI function calling
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "Search the knowledge base for relevant articles and FAQs",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 5
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a new support ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID"
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["email", "whatsapp", "web_form"],
                        "description": "Communication channel"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Ticket subject"
                    },
                    "content": {
                        "type": "string",
                        "description": "Message content"
                    }
                },
                "required": ["customer_id", "channel", "subject", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "escalate_to_human",
            "description": "Escalate a ticket to a human agent",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "integer",
                        "description": "Ticket ID to escalate"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for escalation"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Priority level"
                    }
                },
                "required": ["ticket_id", "reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_history",
            "description": "Get customer's ticket history and information",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "integer",
                        "description": "Customer ID"
                    }
                },
                "required": ["customer_id"]
            }
        }
    }
]
