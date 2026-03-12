"""
WhatsApp Integration using Twilio
This module handles incoming/outgoing WhatsApp messages
"""
import os
from fastapi import APIRouter, Request, Form
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import httpx

load_dotenv()

router = APIRouter()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")

# Initialize Twilio client (only if credentials exist)
twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@router.post("/whatsapp/webhook")
async def whatsapp_webhook(request: Request):
    """
    Twilio webhook endpoint for incoming WhatsApp messages
    This receives form data from Twilio
    """
    form_data = await request.form()
    
    from_number = form_data.get("From", "")
    message_body = form_data.get("Body", "")
    
    if not message_body:
        return MessagingResponse()
    
    # Forward to main API for processing
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/whatsapp",
            json={
                "from_number": from_number,
                "content": message_body
            }
        )
        result = response.json()
    
    # Create Twilio response
    twiml_response = MessagingResponse()
    twiml_response.message(result.get("message", "Thank you for your message."))
    
    return twiml_response

@router.post("/whatsapp/send/{phone_number}")
def send_whatsapp_message(phone_number: str, message: str):
    """
    Send WhatsApp message via Twilio
    Use this for sending responses or notifications
    """
    if not twilio_client:
        return {"error": "Twilio credentials not configured"}
    
    try:
        message = twilio_client.messages.create(
            from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
            body=message,
            to=f'whatsapp:{phone_number}'
        )
        return {"success": True, "message_sid": message.sid}
    except Exception as e:
        return {"success": False, "error": str(e)}
