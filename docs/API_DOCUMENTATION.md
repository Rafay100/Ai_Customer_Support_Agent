# API Documentation

## Base URL
```
http://localhost:8000
```

## Interactive Docs
After starting the server, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Endpoints

### 1. Web Form Submission

**POST** `/api/web-form`

Submit a customer support message via web form.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Shipping Inquiry",
  "message": "How long does shipping take?"
}
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

---

### 2. WhatsApp Message

**POST** `/api/whatsapp`

Receive a WhatsApp message (used by Twilio webhook).

**Request Body:**
```json
{
  "from_number": "+1234567890",
  "content": "I want to return my product"
}
```

**Response:**
```json
{
  "ticket_id": 2,
  "ai_response": "We offer a 30-day return policy...",
  "escalated": false,
  "message": "We offer a 30-day return policy..."
}
```

---

### 3. Email Message

**POST** `/api/email`

Receive an email message (used by Gmail integration).

**Request Body:**
```json
{
  "from_email": "customer@example.com",
  "subject": "Order Status",
  "content": "Where is my order?",
  "in_reply_to": "previous-ticket-id"
}
```

**Response:**
```json
{
  "ticket_id": 3,
  "ai_response": "Once your order ships, you'll receive a tracking number...",
  "escalated": false,
  "message": "Email received. AI response generated."
}
```

---

### 4. List Tickets

**GET** `/api/tickets`

List all tickets (optionally filtered by status).

**Query Parameters:**
- `status` (optional): Filter by status (open, in_progress, resolved, escalated)

**Example:**
```
GET /api/tickets?status=escalated
```

**Response:**
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "status": "escalated",
    "channel": "whatsapp",
    "subject": null,
    "created_at": "2024-01-15T10:30:00Z",
    "assigned_to_human": true
  }
]
```

---

### 5. Get Ticket Details

**GET** `/api/tickets/{ticket_id}`

Get details of a specific ticket.

**Example:**
```
GET /api/tickets/1
```

**Response:**
```json
{
  "id": 1,
  "customer_id": 1,
  "status": "resolved",
  "channel": "web_form",
  "subject": "Shipping Question",
  "created_at": "2024-01-15T10:30:00Z",
  "assigned_to_human": false
}
```

---

### 6. Get Ticket Messages

**GET** `/api/tickets/{ticket_id}/messages`

Get all messages for a specific ticket.

**Example:**
```
GET /api/tickets/1/messages
```

**Response:**
```json
[
  {
    "id": 1,
    "ticket_id": 1,
    "content": "How long does shipping take?",
    "is_from_customer": true,
    "channel": "web_form",
    "created_at": "2024-01-15T10:30:00Z",
    "ai_generated": false
  },
  {
    "id": 2,
    "ticket_id": 1,
    "content": "Standard shipping takes 3-5 business days...",
    "is_from_customer": false,
    "channel": "web_form",
    "created_at": "2024-01-15T10:30:01Z",
    "ai_generated": true
  }
]
```

---

## Webhook Endpoints

### WhatsApp Webhook

**POST** `/whatsapp/webhook`

Twilio webhook endpoint for receiving WhatsApp messages.

**Configuration:**
Set your Twilio webhook URL to:
```
https://your-domain.com/whatsapp/webhook
```

---

### Email Webhook

**POST** `/email/webhook`

Webhook endpoint for email forwarding services.

**Request Body:**
```json
{
  "from": "customer@example.com",
  "subject": "Help Request",
  "body": "I need help with...",
  "in_reply_to": "ticket-reference"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data"
}
```

### 404 Not Found
```json
{
  "detail": "Ticket not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Server Error |

---

## Ticket Statuses

| Status | Description |
|--------|-------------|
| open | New ticket, not yet handled |
| in_progress | Being handled |
| resolved | Issue resolved |
| escalated | Escalated to human agent |

---

## Channel Types

| Channel | Description |
|---------|-------------|
| email | Email messages |
| whatsapp | WhatsApp messages |
| web_form | Web form submissions |

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding:
- Request throttling
- IP-based limits
- API key authentication

---

## Authentication

Currently the API is open for hackathon purposes. For production:
- Add API key authentication
- Implement OAuth2 for admin endpoints
- Add JWT tokens for customer portal

---

## Testing

### Using cURL

**Test Web Form:**
```bash
curl -X POST http://localhost:8000/api/web-form \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test User",
    "email": "test@example.com",
    "subject": "Test",
    "message": "How long does shipping take?"
  }'
```

**Test WhatsApp:**
```bash
curl -X POST http://localhost:8000/api/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "from_number": "+1234567890",
    "content": "I want to return my product"
  }'
```

**Test Email:**
```bash
curl -X POST http://localhost:8000/api/email \
  -H "Content-Type: application/json" \
  -d '{
    "from_email": "test@example.com",
    "subject": "Test",
    "content": "Where is my order?"
  }'
```

**Get Tickets:**
```bash
curl http://localhost:8000/api/tickets
```

---

## Python SDK Example

```python
import requests

API_BASE = "http://localhost:8000"

# Submit web form
response = requests.post(
    f"{API_BASE}/api/web-form",
    json={
        "name": "John Doe",
        "email": "john@example.com",
        "subject": "Question",
        "message": "How long does shipping take?"
    }
)
result = response.json()
print(f"Ticket ID: {result['ticket_id']}")
print(f"Response: {result['ai_response']}")

# Get ticket details
response = requests.get(f"{API_BASE}/api/tickets/{result['ticket_id']}")
ticket = response.json()
print(f"Status: {ticket['status']}")

# Get messages
response = requests.get(f"{API_BASE}/api/tickets/{result['ticket_id']}/messages")
messages = response.json()
for msg in messages:
    print(f"{msg['created_at']}: {msg['content']}")
```

---

## JavaScript Example

```javascript
const API_BASE = 'http://localhost:8000';

// Submit web form
async function submitForm(data) {
  const response = await fetch(`${API_BASE}/api/web-form`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return await response.json();
}

// Get ticket
async function getTicket(ticketId) {
  const response = await fetch(`${API_BASE}/api/tickets/${ticketId}`);
  return await response.json();
}

// Usage
const result = await submitForm({
  name: 'John Doe',
  email: 'john@example.com',
  subject: 'Question',
  message: 'How long does shipping take?'
});

console.log(`Ticket #${result.ticket_id}`);
console.log(`Response: ${result.ai_response}`);
```
