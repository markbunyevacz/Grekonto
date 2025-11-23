"""
Integration Orchestrator - Coordinates all external integrations.

Manages:
- API Gateway
- Jira Integration
- REST Clients
- Integration workflows
- Error handling and recovery
"""

import logging
from typing import Dict, Any, Optional
from .api_gateway import get_gateway, APIResponse
from .jira_integration import JiraIntegrationService, BATicketFormat, IssueType, Priority
from .rest_client import RESTClient
from .circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)


class IntegrationOrchestrator:
    """
    Orchestrates all external integrations.
    
    Provides:
    - Unified integration management
    - Circuit breaker for fault tolerance
    - Error handling and recovery
    - Integration workflows
    """
    
    def __init__(self):
        self.gateway = get_gateway()
        self.jira_service = JiraIntegrationService()
        self.rest_clients: Dict[str, RESTClient] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
    
    def register_rest_client(
        self,
        name: str,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3
    ) -> None:
        """Register a REST client for an external service."""
        client = RESTClient(base_url, timeout=timeout, max_retries=max_retries)
        self.rest_clients[name] = client
        self.circuit_breakers[name] = CircuitBreaker(name=name)
        logger.info(f"Registered REST client: {name}")
    
    def get_rest_client(self, name: str) -> Optional[RESTClient]:
        """Get a registered REST client."""
        return self.rest_clients.get(name)
    
    def create_jira_ticket(
        self,
        summary: str,
        description: str,
        issue_type: IssueType = IssueType.STORY,
        priority: Priority = Priority.MEDIUM
    ) -> APIResponse:
        """
        Create a Jira ticket with BA-specific fields.
        
        Returns APIResponse with ticket details or error.
        """
        try:
            # Check circuit breaker
            breaker = self.circuit_breakers.get("jira")
            if breaker and breaker.is_open():
                return self.gateway.service_unavailable_response("Jira")
            
            # Create ticket
            ticket = BATicketFormat(summary, description, issue_type, priority)
            result = self.jira_service.create_ticket(ticket)
            
            if result.get("success"):
                return self.gateway.created_response(
                    data={
                        "ticket_key": result.get("ticket_key"),
                        "ticket_id": result.get("ticket_id"),
                        "url": result.get("url")
                    },
                    message="Jira ticket created successfully"
                )
            else:
                if breaker:
                    breaker.record_failure()
                return self.gateway.error_response(
                    error=result.get("error", "Failed to create ticket"),
                    status_code=500
                )
        
        except Exception as e:
            logger.error(f"Error creating Jira ticket: {e}")
            if breaker:
                breaker.record_failure()
            return self.gateway.internal_error_response(str(e))
    
    def update_jira_ticket(
        self,
        ticket_key: str,
        updates: Dict[str, Any]
    ) -> APIResponse:
        """Update a Jira ticket."""
        try:
            breaker = self.circuit_breakers.get("jira")
            if breaker and breaker.is_open():
                return self.gateway.service_unavailable_response("Jira")
            
            result = self.jira_service.update_ticket(ticket_key, updates)
            
            if result.get("success"):
                return self.gateway.success_response(
                    data={"ticket_key": ticket_key},
                    message="Jira ticket updated successfully"
                )
            else:
                if breaker:
                    breaker.record_failure()
                return self.gateway.error_response(
                    error=result.get("error", "Failed to update ticket"),
                    status_code=500
                )
        
        except Exception as e:
            logger.error(f"Error updating Jira ticket: {e}")
            if breaker:
                breaker.record_failure()
            return self.gateway.internal_error_response(str(e))
    
    def call_external_api(
        self,
        client_name: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """
        Call an external API through a registered REST client.
        
        Supports: GET, POST, PUT, PATCH, DELETE
        """
        try:
            client = self.get_rest_client(client_name)
            if not client:
                return self.gateway.error_response(
                    error=f"REST client '{client_name}' not found",
                    status_code=404
                )
            
            breaker = self.circuit_breakers.get(client_name)
            if breaker and breaker.is_open():
                return self.gateway.service_unavailable_response(client_name)
            
            # Make request
            method_lower = method.lower()
            if method_lower == "get":
                result = client.get(endpoint, headers=headers)
            elif method_lower == "post":
                result = client.post(endpoint, data or {}, headers=headers)
            elif method_lower == "put":
                result = client.put(endpoint, data or {}, headers=headers)
            elif method_lower == "patch":
                result = client.patch(endpoint, data or {}, headers=headers)
            elif method_lower == "delete":
                result = client.delete(endpoint, headers=headers)
            else:
                return self.gateway.error_response(
                    error=f"Unsupported HTTP method: {method}",
                    status_code=400
                )
            
            if breaker:
                breaker.record_success()
            
            return self.gateway.success_response(data=result)
        
        except Exception as e:
            logger.error(f"Error calling external API: {e}")
            breaker = self.circuit_breakers.get(client_name)
            if breaker:
                breaker.record_failure()
            return self.gateway.internal_error_response(str(e))
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all integrations."""
        status = {
            "jira": {
                "configured": self.jira_service.api_token is not None,
                "circuit_breaker": "CLOSED"
            },
            "rest_clients": {}
        }
        
        for name, breaker in self.circuit_breakers.items():
            status["rest_clients"][name] = {
                "registered": name in self.rest_clients,
                "circuit_breaker": breaker.state.value
            }
        
        return status


# Global orchestrator instance
_orchestrator: Optional[IntegrationOrchestrator] = None


def get_orchestrator() -> IntegrationOrchestrator:
    """Get or create the global integration orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = IntegrationOrchestrator()
    return _orchestrator

