# 🚀 Quick Start Guide

## Step-by-Step Setup (5 Minutes)

### 1️⃣ Install Python Dependencies
```bash
# Option A: Use setup script (Windows)
setup.bat

# Option B: Manual installation
pip install -r requirements.txt
```

### 2️⃣ Setup PostgreSQL Database

**Option A: Using pgAdmin**
1. Open pgAdmin
2. Right-click "Databases" → "Create" → "Database"
3. Name: `customer_support`
4. Save

**Option B: Using Command Line**
```bash
createdb customer_support
```

**Option C: Using psql**
```sql
CREATE DATABASE customer_support;
```

### 3️⃣ Configure Environment

Edit `.env` file:
```env
# Update database password
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/customer_support

# Optional: Add OpenAI key for advanced AI
OPENAI_API_KEY=sk-...

# Optional: Twilio for WhatsApp
TWILIO_ACCOUNT_SID=...
TWILIO_AUTH_TOKEN=...
```

### 4️⃣ Run the Application

**Option A: Use run script (Windows)**
```bash
run.bat
```

**Option B: Manual start**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5️⃣ Test It!

**Open in browser:**
- API Docs: http://localhost:8000/docs
- Web Form: http://localhost:8000/static/index.html

**Test with cURL:**
```bash
curl -X POST http://localhost:8000/api/web-form \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test\",\"email\":\"test@example.com\",\"subject\":\"Hi\",\"message\":\"How long does shipping take?\"}"
```

---

## ✅ Verification Checklist

- [ ] Server starts without errors
- [ ] Can access http://localhost:8000/docs
- [ ] Can submit web form
- [ ] Database tables created automatically
- [ ] Can view tickets at `/api/tickets`

---

## 🎯 Demo Flow

### Demo 1: AI Handles Simple Query
1. Open http://localhost:8000/static/index.html
2. Fill form:
   - Name: John Doe
   - Email: john@example.com
   - Subject: Shipping Question
   - Message: How long does shipping take?
3. Submit → See AI response instantly
4. Check ticket created in database

### Demo 2: Escalation to Human
1. Open web form again
2. Fill form:
   - Message: I'm very angry about the delay!
3. Submit → See escalation message
4. Check ticket status = "escalated"

### Demo 3: API Testing
1. Open http://localhost:8000/docs
2. Try POST `/api/whatsapp`
3. Enter test phone number and message
4. See response with ticket ID

---

## 🐛 Troubleshooting

### "Database connection error"
```bash
# Check PostgreSQL is running
# Verify DATABASE_URL in .env
# Make sure database 'customer_support' exists
```

### "Module not found"
```bash
# Make sure virtual environment is activated
# Reinstall dependencies:
pip install -r requirements.txt
```

### "Port 8000 already in use"
```bash
# Kill process on port 8000
# Or use different port:
python -m uvicorn app.main:app --reload --port 8001
```

---

## 📊 What You Built

```
✅ Multi-channel support (Email, WhatsApp, Web)
✅ AI-powered FAQ matching
✅ Smart escalation rules
✅ PostgreSQL ticket system
✅ RESTful API
✅ Beautiful web form
✅ Complete documentation
```

---

## 🎓 Next Steps

### For Hackathon Demo:
1. ✅ Run `setup.bat`
2. ✅ Start server with `run.bat`
3. ✅ Open web form in browser
4. ✅ Submit test messages
5. ✅ Show API docs to judges

### For Production:
1. Deploy to cloud (Heroku, AWS, etc.)
2. Set up real Twilio account
3. Configure Gmail API
4. Add authentication
5. Set up monitoring

---

## 💡 Pro Tips

**Impress Judges:**
- Show the architecture diagram
- Demonstrate both AI handling and escalation
- Explain the routing rules
- Show database schema
- Mention scalability (Kafka, Docker)

**Bonus Points:**
- Add more FAQs to knowledge base
- Customize escalation rules
- Add sentiment analysis demo
- Show channel-specific formatting

---

**Good luck with your hackathon! 🚀**
