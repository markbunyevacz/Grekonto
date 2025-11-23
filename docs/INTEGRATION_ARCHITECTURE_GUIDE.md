# Integration Architecture - Complete Guide

**Projekt**: Grekonto AI Automatizáció  
**Verzió**: 1.0
**Utolsó frissítés**: 2025-11-23
**Commit**: TBD

## 🎯 Quick Start

### 1. Import Required Modules

```python
from shared.api_gateway import get_gateway
from shared.integration_orchestrator import get_orchestrator
from shared.jira_integration import BATicketFormat, IssueType, Priority
from shared.rest_client import RESTClient
```

### 2. Create Jira Ticket with BA Fields

```python
orchestrator = get_orchestrator()

# Create ticket with BA-specific fields
response = orchestrator.create_jira_ticket(
    summary="Implement user authentication",
    description="Add OAuth 2.0 support",
    issue_type=IssueType.STORY,
    priority=Priority.HIGH
)

if response.status_code == 201:
    ticket_key = response.data['ticket_key']
    print(f"✅ Ticket created: {ticket_key}")
else:
    print(f"❌ Error: {response.error}")
```

### 3. Register and Call External API

```python
orchestrator = get_orchestrator()

# Register external API
orchestrator.register_rest_client(
    "external_api",
    "https://api.external.com",
    timeout=30,
    max_retries=3
)

# Call API
response = orchestrator.call_external_api(
    client_name="external_api",
    method="GET",
    endpoint="/users/1"
)

if response.status_code == 200:
    user_data = response.data
    print(f"User: {user_data}")
```

### 4. Handle API Responses

```python
gateway = get_gateway()

# Success response
response = gateway.success_response(
    data={"id": 1, "name": "Test"},
    message="Operation successful"
)

# Error response
response = gateway.error_response(
    error="Invalid input",
    status_code=400
)

# Convert to JSON
json_response = response.to_json()
```

## 🔄 Common Patterns

### Pattern 1: Complete Jira Workflow

```python
from shared.integration_orchestrator import get_orchestrator
from shared.jira_integration import IssueType, Priority

orchestrator = get_orchestrator()

# Create ticket
ticket_response = orchestrator.create_jira_ticket(
    summary="Implement feature X",
    description="Feature description",
    issue_type=IssueType.STORY,
    priority=Priority.HIGH
)

if ticket_response.status_code == 201:
    ticket_key = ticket_response.data['ticket_key']
    
    # Update ticket
    update_response = orchestrator.update_jira_ticket(
        ticket_key=ticket_key,
        updates={"status": "In Progress"}
    )
    
    if update_response.status_code == 200:
        print(f"✅ Ticket updated: {ticket_key}")
```

### Pattern 2: BA Ticket with All Fields

```python
from shared.jira_integration import BATicketFormat, IssueType, Priority

ticket = BATicketFormat(
    summary="Implement payment processing",
    description="Add payment gateway integration",
    issue_type=IssueType.STORY,
    priority=Priority.HIGH
)

# Add BA-specific fields
ticket.add_business_value("Enable online payments, increase revenue")
ticket.add_assumption("Payment gateway API is available")
ticket.add_assumption("PCI compliance is handled by provider")
ticket.add_non_functional_requirement("Response time < 2 seconds")
ticket.add_non_functional_requirement("99.9% uptime")
ticket.add_acceptance_criterion("User can process payment")
ticket.add_acceptance_criterion("Payment confirmation is sent")
ticket.add_dependency("Payment gateway account setup")
ticket.add_stakeholder("Finance team")
ticket.add_stakeholder("Security team")
ticket.set_estimated_effort("8 points")
ticket.add_label("payment")
ticket.add_label("integration")

# Create in Jira
service = JiraIntegrationService()
result = service.create_ticket(ticket)
```

### Pattern 3: Error Handling with Circuit Breaker

```python
orchestrator = get_orchestrator()

# Register API with circuit breaker
orchestrator.register_rest_client("flaky_api", "https://api.flaky.com")

# Call API - circuit breaker handles failures
response = orchestrator.call_external_api(
    client_name="flaky_api",
    method="GET",
    endpoint="/data"
)

if response.status_code == 503:
    print("Service temporarily unavailable (circuit breaker open)")
elif response.status_code == 200:
    print(f"Data: {response.data}")
else:
    print(f"Error: {response.error}")
```

### Pattern 4: REST Client with Retry Logic

```python
from shared.rest_client import RESTClient

client = RESTClient(
    base_url="https://api.example.com",
    timeout=30,
    max_retries=3,
    backoff_factor=0.5
)

# Automatic retry on 5xx errors
try:
    result = client.get("/users/1")
    print(f"User: {result}")
except Exception as e:
    print(f"Error after retries: {e}")

# Check request history
history = client.get_request_history()
for request in history:
    print(f"{request['method']} {request['url']} - {request['status_code']}")
```

## 📊 HTTP Status Codes

| Code | Meaning | Use Case |
|------|---------|----------|
| 200 | OK | Successful GET/PUT/PATCH |
| 201 | Created | Successful POST |
| 202 | Accepted | Request accepted for processing |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Authentication failed |
| 403 | Forbidden | Access denied |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict |
| 429 | Rate Limited | Too many requests |
| 500 | Internal Error | Server error |
| 503 | Unavailable | Service unavailable |

## 🏆 Best Practices

1. **Always check status code** - Verify response.status_code before using data
2. **Use circuit breakers** - Prevent cascading failures
3. **Implement retry logic** - Handle transient failures
4. **Log all requests** - Track integration issues
5. **Validate input** - Check data before sending
6. **Handle errors gracefully** - Provide meaningful error messages
7. **Monitor integrations** - Track success/failure rates
8. **Use BA fields** - Include business context in tickets

---

## DOKUMENTÁCIÓ VERZIÓ ÉS FRISSÍTÉSI TÖRTÉNET

**Verzió:** 1.0  
**Utolsó frissítés:** 2025-11-23  
**Commit:** TBD

