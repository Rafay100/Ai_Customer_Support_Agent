from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from datetime import datetime
import sqlite3
from pathlib import Path

app = FastAPI(title="AI Customer Support")

# Get static directory
STATIC_DIR = Path(__file__).parent / "app" / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
def init_db():
    conn = sqlite3.connect("support.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        subject TEXT,
        message TEXT,
        response TEXT,
        escalated INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

# Simple AI responses
FAQS = {
    "shipping": "Standard shipping takes 3-5 business days. Express shipping (1-2 business days) is available for an additional fee.",
    "return": "We offer a 30-day return policy for all unused items in original packaging. Refunds are processed within 5-7 business days.",
    "payment": "We accept all major credit cards (Visa, MasterCard, Amex), PayPal, and bank transfers.",
    "track": "Once your order ships, you'll receive a tracking number via email. Use it on our website to track your order.",
    "cancel": "Orders can be cancelled within 24 hours of placement. After that, the returns process applies."
}

ESCALATE_WORDS = ["angry", "frustrated", "terrible", "horrible", "manager", "human", "refund", "complaint"]

def get_ai_response(message):
    message_lower = message.lower()
    
    # Check for escalation
    for word in ESCALATE_WORDS:
        if word in message_lower:
            return None, True  # Escalate
    
    # Find matching FAQ
    for keyword, answer in FAQS.items():
        if keyword in message_lower:
            return answer, False
    
    # Default response
    return "Thank you for your message. Our team will respond shortly.", False

class SupportForm(BaseModel):
    name: str
    email: str
    subject: str
    message: str

@app.get("/")
async def root():
    try:
        index_file = STATIC_DIR / "index.html"
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
        return HTMLResponse("<h1>UI not found</h1>", status_code=404)
    except Exception as e:
        return HTMLResponse(f"<h1>Error: {str(e)}</h1>", status_code=500)

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/api/web-form")
async def submit_form(form: SupportForm):
    try:
        # Get AI response
        response, escalated = get_ai_response(form.message)
        
        # Save to database
        conn = sqlite3.connect("support.db")
        c = conn.cursor()
        c.execute(
            "INSERT INTO tickets (name, email, subject, message, response, escalated) VALUES (?, ?, ?, ?, ?, ?)",
            (form.name, form.email, form.subject, form.message, response, 1 if escalated else 0)
        )
        ticket_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return {
            "ticket_id": ticket_id,
            "ai_response": response,
            "escalated": escalated,
            "message": "Ticket created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/tickets")
async def get_tickets():
    conn = sqlite3.connect("support.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM tickets ORDER BY created_at DESC")
    tickets = [dict(row) for row in c.fetchall()]
    conn.close()
    return tickets

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
