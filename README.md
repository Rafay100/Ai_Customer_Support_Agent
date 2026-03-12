# 🤖 AI Customer Support Agent

Multi-channel AI-powered customer support system for handling customer queries via **Email**, **WhatsApp**, and **Web Form**.

## 📋 Features

✅ **Multi-Channel Support**
- 📧 Email (Gmail API)
- 💬 WhatsApp (Twilio)
- 🌐 Web Form (React/HTML)

✅ **AI-Powered Responses**
- FAQ matching with keyword detection
- Automatic response generation
- Channel-specific formatting

✅ **Smart Routing**
- AI handles common queries
- Automatic escalation for complex issues
- Priority-based ticket routing

✅ **Ticket Management**
- PostgreSQL database
- Complete message history
- Customer tracking

✅ **Modern Tech Stack**
- FastAPI backend
- SQLAlchemy ORM
- RESTful API design

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Customer Channels                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  Email   │  │ WhatsApp │  │ Web Form │              │
│  │ (Gmail)  │  │ (Twilio) │  │  (HTML)  │              │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       │             │             │                     │
│       └─────────────┼─────────────┘                     │
│                     │                                   │
│              ┌──────▼──────┐                           │
│              │  FastAPI    │                           │
│              │   Server    │                           │
│              └──────┬──────┘                           │
│                     │                                   │
│       ┌─────────────┼─────────────┐                    │
│       │             │             │                    │
│  ┌────▼─────┐  ┌────▼─────┐  ┌────▼─────┐             │
│  │   AI     │  │ Routing  │  │  Ticket  │             │
│  │  Engine  │  │  Rules   │  │  System  │             │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘             │
│       │             │             │                    │
│       └─────────────┼─────────────┘                    │
│                     │                                   │
│              ┌──────▼──────┐                           │
│              │ PostgreSQL  │                           │
│              │  Database   │                           │
│              └─────────────┘                           │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL
- Internet connection

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment Variables
```bash
# Copy example env file
copy .env.example .env

# Edit .env with your credentials
```

### 3. Setup PostgreSQL Database
```bash
# Create database
createdb customer_support

# Or using psql
psql -U postgres
CREATE DATABASE customer_support;
```

### 4. Run the Application
```bash
# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or simply
python app/main.py
```

### 5. Access the Application
- **API Docs**: http://localhost:8000/docs
- **Web Form**: http://localhost:8000/static/index.html
- **Health Check**: http://localhost:8000/health

---

## 📁 Project Structure

```
AI_Customer_Support_Agent/
│
├── app/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── schemas.py         # Pydantic models
│   │
│   ├── channels/
│   │   ├── email_channel.py   # Gmail integration
│   │   └── whatsapp_channel.py # Twilio integration
│   │
│   ├── core/
│   │   └── knowledge_base.py  # FAQ database
│   │
│   ├── db/
│   │   └── database.py        # DB connection
│   │
│   ├── models/
│   │   └── models.py          # SQLAlchemy models
│   │
│   ├── services/
│   │   ├── ai_engine.py       # AI response engine
│   │   └── routing_rules.py   # Escalation logic
│   │
│   ├── static/
│   │   └── index.html         # Web form UI
│   │
│   └── main.py                # FastAPI app
│
├── tests/
│   └── test_api.py            # API tests
│
├── docs/
│   └── API_DOCUMENTATION.md   # Detailed API docs
│
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## 🔌 API Endpoints

### Customer-Facing APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/web-form` | Submit web form message |
| POST | `/api/whatsapp` | Receive WhatsApp message |
| POST | `/api/email` | Receive email message |

### Admin APIs

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tickets` | List all tickets |
| GET | `/api/tickets/{id}` | Get ticket details |
| GET | `/api/tickets/{id}/messages` | Get ticket messages |

### Webhook Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/whatsapp/webhook` | Twilio webhook |
| POST | `/email/webhook` | Email webhook |

---

## 📝 API Usage Examples

### 1. Web Form Submission
```bash
curl -X POST http://localhost:8000/api/web-form \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Shipping Question",
    "message": "How long does shipping take?"
  }'
```

**Response:**
```json
{
  "ticket_id": 1,
  "ai_response": "Standard shipping takes 3-5 business days...",
  "escalated": false,
  "message": "Ticket created. AI response sent."
}
```

### 2. WhatsApp Message
```bash
curl -X POST http://localhost:8000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+1234567890",
    "content": "I want to return my product"
  }'
```

### 3. Email Message
```bash
curl -X POST http://localhost:8000/api/email \
  -H "Content-Type: application/json" \
  -d '{
    "from_email": "customer@example.com",
    "subject": "Order Issue",
    "content": "My order hasn't arrived yet"
  }'
```

---

## 🧠 AI Engine

### How It Works

1. **Message Received** → Customer sends message via any channel
2. **FAQ Matching** → AI searches knowledge base for best match
3. **Routing Decision** → Check if escalation needed
4. **Response Generation** → Format response for channel
5. **Save to Database** → Store ticket and messages

### Escalation Rules

Messages are escalated to humans when they contain:
- 😠 **Complaint keywords**: angry, frustrated, terrible, etc.
- ⚡ **Urgent keywords**: urgent, ASAP, emergency, etc.
- 💰 **Pricing issues**: refund, chargeback, billing, etc.
- 👤 **Human request**: manager, supervisor, real person, etc.

### Channel-Specific Responses

| Channel | Max Length | Tone | Emoji |
|---------|------------|------|-------|
| WhatsApp | 160 chars | Casual | ✅ |
| Email | 1000 chars | Formal | ❌ |
| Web Form | 500 chars | Professional | ❌ |

---

## 🗄️ Database Schema

### Tables

**Customers**
- id, name, email, phone, created_at

**Tickets**
- id, customer_id, status, channel, subject, created_at, assigned_to_human

**Messages**
- id, ticket_id, content, is_from_customer, channel, created_at, ai_generated

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/customer_support

# OpenAI (Optional - for advanced AI)
OPENAI_API_KEY=your_key_here

# Twilio (WhatsApp)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_NUMBER=+14155238886

# Gmail API
GMAIL_CLIENT_ID=your_client_id
GMAIL_CLIENT_SECRET=your_secret
GMAIL_REDIRECT_URI=http://localhost:8000/callback
```

---

## 🧪 Testing

### Test AI Engine
```bash
python app/services/ai_engine.py
```

### Test Routing Rules
```bash
python app/services/routing_rules.py
```

### Run API Tests
```bash
pytest tests/
```

---

## 🎯 Demo Scenarios

### Scenario 1: Simple FAQ (AI Handles)
```
Customer: "How long does shipping take?"
AI: "Standard shipping takes 3-5 business days..."
Status: ✅ Resolved by AI
```

### Scenario 2: Complaint (Escalated)
```
Customer: "I'm very angry about the delay!"
AI: "I understand this needs personal attention..."
Status: 🔴 Escalated to human
```

### Scenario 3: Pricing Query (Escalated)
```
Customer: "Can I get a discount?"
AI: "Let me connect you with a support agent..."
Status: 🟡 Escalated to human
```

---

## 🚀 Deployment

### Docker (Optional)
```bash
# Build image
docker build -t ai-support-agent .

# Run container
docker run -p 8000:8000 --env-file .env ai-support-agent
```

### Production Checklist
- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Set up SSL/HTTPS
- [ ] Configure Twilio webhook
- [ ] Set up Gmail API credentials
- [ ] Enable logging
- [ ] Set up monitoring

---

## 📊 What Judges Will See

✅ **Multi-channel support** - Email, WhatsApp, Web Form  
✅ **AI-powered responses** - FAQ matching + smart routing  
✅ **Ticket system** - All messages saved in PostgreSQL  
✅ **Escalation logic** - AI vs Human decision making  
✅ **Clean architecture** - Modular, scalable design  
✅ **API documentation** - Interactive Swagger UI  
✅ **Working prototype** - Ready to demo  

---

## 🎓 Learning Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://www.sqlalchemy.org/
- **Twilio WhatsApp**: https://www.twilio.com/whatsapp
- **Gmail API**: https://developers.google.com/gmail/api

---

## 📄 License

MIT License - Built for Hackathon 5

---

## 👥 Team

Built with ❤️ for AI Customer Support Hackathon

**Need Help?** Check `/docs` folder for detailed documentation or open `/docs` in browser after running the server.
"# Ai_Customer_Support_Agent" 
