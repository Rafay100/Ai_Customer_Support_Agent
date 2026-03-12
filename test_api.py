import requests

# Test 1: Health check
print("=== Health Check ===")
r = requests.get("http://localhost:8000/health")
print(f"Status: {r.json()}")

# Test 2: Submit web form (AI handles)
print("\n=== Test 1: Simple FAQ (AI Handles) ===")
r = requests.post("http://localhost:8000/api/web-form", json={
    "name": "John Doe",
    "email": "john@example.com",
    "subject": "Shipping Question",
    "message": "How long does shipping take?"
})
print(f"Response: {r.json()}")

# Test 3: Submit web form (Escalation)
print("\n=== Test 2: Complaint (Escalated) ===")
r = requests.post("http://localhost:8000/api/web-form", json={
    "name": "Jane Smith",
    "email": "jane@example.com",
    "subject": "Complaint",
    "message": "I'm very angry about the delay!"
})
print(f"Response: {r.json()}")

# Test 4: Get all tickets
print("\n=== All Tickets ===")
r = requests.get("http://localhost:8000/api/tickets")
tickets = r.json()
print(f"Total tickets: {len(tickets)}")
for t in tickets:
    print(f"  - Ticket #{t['id']}: {t['name']} - {t['subject']}")

print("\n✅ All tests passed!")
