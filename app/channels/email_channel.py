"""
Gmail Integration for receiving customer emails
Uses Gmail API to fetch and send emails
"""
import os
import base64
from typing import List, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
import httpx

load_dotenv()

# Gmail API Scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.send']

class GmailIntegration:
    def __init__(self):
        self.creds = None
        self.service = None
        self.setup_complete = False
        
        # Check if credentials exist
        self.client_id = os.getenv("GMAIL_CLIENT_ID")
        self.client_secret = os.getenv("GMAIL_CLIENT_SECRET")
        self.redirect_uri = os.getenv("GMAIL_REDIRECT_URI")
        
        if self.client_id and self.client_secret:
            self.setup_complete = True
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # For production, use web flow instead
                flow = InstalledAppFlow.from_client_config({
                    "installed": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                }, SCOPES)
                self.creds = flow.run_local_server(port=8080)
            
            # Save credentials
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('gmail', 'v1', credentials=self.creds)
        return self.service
    
    def fetch_recent_emails(self, max_results: int = 10) -> List[dict]:
        """Fetch recent emails from inbox"""
        if not self.service:
            self.authenticate()
        
        messages = []
        results = self.service.users().messages().list(
            userId='me', 
            labelIds=['INBOX'],
            maxResults=max_results
        ).execute()
        
        msgs = results.get('messages', [])
        
        for msg in msgs:
            message = self.service.users().messages().get(
                userId='me', 
                id=msg['id']
            ).execute()
            
            # Parse email
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
            
            # Get body
            body = self._get_email_body(message)
            
            messages.append({
                'id': message['id'],
                'from': from_email,
                'subject': subject,
                'body': body
            })
        
        return messages
    
    def _get_email_body(self, message: dict) -> str:
        """Extract body from email message"""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = part['body']['data']
                    return base64.urlsafe_b64decode(body).decode('utf-8')
        elif 'body' in message['payload']:
            body = message['payload']['body']['data']
            return base64.urlsafe_b64decode(body).decode('utf-8')
        
        return ""
    
    def send_email(self, to: str, subject: str, body: str, in_reply_to: str = None):
        """Send email via Gmail"""
        if not self.service:
            self.authenticate()
        
        from_email = os.getenv("GMAIL_ADDRESS", "support@company.com")
        
        # Create message
        message = self._create_message(from_email, to, subject, body, in_reply_to)
        
        # Send message
        sent_message = self.service.users().messages().send(
            userId='me', 
            body=message
        ).execute()
        
        return sent_message
    
    def _create_message(self, sender: str, to: str, subject: str, text: str, in_reply_to: str = None):
        """Create email message"""
        from email.mime.text import MIMEText
        from email.header import Header
        
        message = MIMEText(text)
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        
        if in_reply_to:
            message['In-Reply-To'] = in_reply_to
            message['References'] = in_reply_to
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}


# Simple webhook receiver for emails
from fastapi import APIRouter

router = APIRouter()

@router.post("/email/webhook")
async def email_webhook(email_data: dict):
    """
    Webhook endpoint for receiving emails
    Can be used with email forwarding services
    """
    from_email = email_data.get("from", "")
    subject = email_data.get("subject", "")
    content = email_data.get("body", "")
    in_reply_to = email_data.get("in_reply_to")
    
    # Forward to main API
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/email",
            json={
                "from_email": from_email,
                "subject": subject,
                "content": content,
                "in_reply_to": in_reply_to
            }
        )
        result = response.json()
    
    return {"status": "processed", "result": result}
