"""
Test suite for AI Customer Support Agent
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Customer Support" in response.json()["message"]

def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_web_form_submission():
    """Test web form message submission"""
    response = client.post(
        "/api/web-form",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Shipping Question",
            "message": "How long does shipping take?"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "ticket_id" in data
    assert "ai_response" in data or "escalated" in data

def test_whatsapp_message():
    """Test WhatsApp message submission"""
    response = client.post(
        "/api/whatsapp",
        json={
            "from_number": "+1234567890",
            "content": "I want to return my product"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "ticket_id" in data
    assert "message" in data

def test_email_message():
    """Test email message submission"""
    response = client.post(
        "/api/email",
        json={
            "from_email": "customer@example.com",
            "subject": "Order Help",
            "content": "Where is my order?"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "ticket_id" in data

def test_escalation_detection():
    """Test that angry messages are escalated"""
    response = client.post(
        "/api/whatsapp",
        json={
            "from_number": "+1234567890",
            "content": "I'm very angry about this terrible service!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["escalated"] == True

def test_ai_handling():
    """Test that simple FAQs are handled by AI"""
    response = client.post(
        "/api/web-form",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Question",
            "message": "What payment methods do you accept?"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["escalated"] == False
    assert data["ai_response"] is not None

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
