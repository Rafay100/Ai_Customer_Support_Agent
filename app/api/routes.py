from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import Customer, Ticket, Message, ChannelType, TicketStatus
from app.api.schemas import WebFormMessage, WhatsAppMessage, EmailMessage, SupportResponse
from app.services.ai_engine import AIEngine

router = APIRouter()
ai_engine = AIEngine()

def get_or_create_customer(db: Session, email: str = None, phone: str = None, name: str = None):
    """Get existing customer or create new one"""
    if email:
        customer = db.query(Customer).filter(Customer.email == email).first()
        if customer:
            return customer
    if phone:
        customer = db.query(Customer).filter(Customer.phone == phone).first()
        if customer:
            return customer
    
    # Create new customer
    customer = Customer(name=name, email=email, phone=phone)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer

def create_ticket(db: Session, customer_id: int, channel: ChannelType, subject: str = None):
    """Create a new support ticket"""
    ticket = Ticket(
        customer_id=customer_id,
        channel=channel,
        subject=subject,
        status=TicketStatus.OPEN
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket

@router.post("/web-form", response_model=SupportResponse)
def receive_web_form_message(form_data: WebFormMessage, db: Session = Depends(get_db)):
    """Receive message from web contact form"""
    try:
        # Get or create customer
        customer = get_or_create_customer(db, email=form_data.email, name=form_data.name)
        
        # Create ticket
        ticket = create_ticket(db, customer.id, ChannelType.WEB_FORM, form_data.subject)
        
        # Save customer message
        customer_message = Message(
            ticket_id=ticket.id,
            content=form_data.message,
            is_from_customer=True,
            channel=ChannelType.WEB_FORM
        )
        db.add(customer_message)
        db.commit()
        
        # Generate AI response
        ai_result = ai_engine.generate_response(form_data.message, "web_form")
        
        # Update ticket if escalation needed
        if ai_result["should_escalate"]:
            ticket.status = TicketStatus.ESCALATED
            ticket.assigned_to_human = True
            db.commit()
        
        # Save AI response if not escalating
        if not ai_result["should_escalate"]:
            ai_message = Message(
                ticket_id=ticket.id,
                content=ai_result["response"],
                is_from_customer=False,
                channel=ChannelType.WEB_FORM,
                ai_generated=True
            )
            db.add(ai_message)
            db.commit()
        
        return SupportResponse(
            ticket_id=ticket.id,
            ai_response=ai_result["response"] if not ai_result["should_escalate"] else None,
            escalated=ai_result["should_escalate"],
            message="Ticket created. " + ("Escalated to human agent." if ai_result["should_escalate"] else "AI response sent.")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/whatsapp", response_model=SupportResponse)
def receive_whatsapp_message(msg: WhatsAppMessage, db: Session = Depends(get_db)):
    """Receive message from WhatsApp"""
    try:
        # Get or create customer
        customer = get_or_create_customer(db, phone=msg.from_number)
        
        # Create ticket
        ticket = create_ticket(db, customer.id, ChannelType.WHATSAPP)
        
        # Save customer message
        customer_message = Message(
            ticket_id=ticket.id,
            content=msg.content,
            is_from_customer=True,
            channel=ChannelType.WHATSAPP
        )
        db.add(customer_message)
        db.commit()
        
        # Generate AI response
        ai_result = ai_engine.generate_response(msg.content, "whatsapp")
        
        # Update ticket if escalation needed
        if ai_result["should_escalate"]:
            ticket.status = TicketStatus.ESCALATED
            ticket.assigned_to_human = True
            db.commit()
        
        # Save AI response if not escalating
        if not ai_result["should_escalate"]:
            ai_message = Message(
                ticket_id=ticket.id,
                content=ai_result["response"],
                is_from_customer=False,
                channel=ChannelType.WHATSAPP,
                ai_generated=True
            )
            db.add(ai_message)
            db.commit()
        
        return SupportResponse(
            ticket_id=ticket.id,
            ai_response=ai_result["response"],
            escalated=ai_result["should_escalate"],
            message=ai_result["response"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/email", response_model=SupportResponse)
def receive_email_message(email_data: EmailMessage, db: Session = Depends(get_db)):
    """Receive message from Gmail"""
    try:
        # Get or create customer
        customer = get_or_create_customer(db, email=email_data.from_email)
        
        # Create ticket
        ticket = create_ticket(db, customer.id, ChannelType.EMAIL, email_data.subject)
        
        # Save customer message
        customer_message = Message(
            ticket_id=ticket.id,
            content=email_data.content,
            is_from_customer=True,
            channel=ChannelType.EMAIL
        )
        db.add(customer_message)
        db.commit()
        
        # Generate AI response
        ai_result = ai_engine.generate_response(email_data.content, "email")
        
        # Update ticket if escalation needed
        if ai_result["should_escalate"]:
            ticket.status = TicketStatus.ESCALATED
            ticket.assigned_to_human = True
            db.commit()
        
        # Save AI response if not escalating
        if not ai_result["should_escalate"]:
            ai_message = Message(
                ticket_id=ticket.id,
                content=ai_result["response"],
                is_from_customer=False,
                channel=ChannelType.EMAIL,
                ai_generated=True
            )
            db.add(ai_message)
            db.commit()
        
        return SupportResponse(
            ticket_id=ticket.id,
            ai_response=ai_result["response"] if not ai_result["should_escalate"] else None,
            escalated=ai_result["should_escalate"],
            message="Email received. " + ("Escalated to human agent." if ai_result["should_escalate"] else "AI response generated.")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tickets")
def list_tickets(db: Session = Depends(get_db)):
    """List all tickets"""
    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all()
    return tickets

@router.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    """Get ticket details"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.get("/tickets/{ticket_id}/messages")
def get_ticket_messages(ticket_id: int, db: Session = Depends(get_db)):
    """Get all messages for a ticket"""
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket.messages
