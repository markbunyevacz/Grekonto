"""
Tests for Integration Architecture.

Tests API Gateway, Jira Integration, REST Client, and Integration Orchestrator.
"""

import sys
import os
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.api_gateway import APIGateway, APIResponse, HTTPStatusCode
from shared.jira_integration import BATicketFormat, IssueType, Priority, JiraIntegrationService
from shared.rest_client import RESTClient
from shared.integration_orchestrator import IntegrationOrchestrator


class TestAPIGateway(unittest.TestCase):
    """Test API Gateway."""
    
    def setUp(self):
        self.gateway = APIGateway()
    
    def test_success_response(self):
        """Test success response creation."""
        response = self.gateway.success_response(
            data={"id": 1, "name": "Test"},
            message="Success"
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.to_dict()["success"])
        self.assertEqual(response.data["id"], 1)
    
    def test_error_response(self):
        """Test error response creation."""
        response = self.gateway.error_response(
            error="Invalid input",
            status_code=400
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.to_dict()["success"])
        self.assertEqual(response.error, "Invalid input")
    
    def test_created_response(self):
        """Test 201 Created response."""
        response = self.gateway.created_response(
            data={"id": 1}
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.to_dict()["success"])
    
    def test_not_found_response(self):
        """Test 404 Not Found response."""
        response = self.gateway.not_found_response("User", "123")
        
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response.to_dict()["success"])
    
    def test_rate_limited_response(self):
        """Test 429 Rate Limited response."""
        response = self.gateway.rate_limited_response(60)
        
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.metadata["retry_after"], 60)
    
    def test_response_to_json(self):
        """Test response serialization to JSON."""
        response = self.gateway.success_response(data={"test": "data"})
        json_str = response.to_json()
        
        self.assertIn("status_code", json_str)
        self.assertIn("success", json_str)
        self.assertIn("test", json_str)


class TestBATicketFormat(unittest.TestCase):
    """Test BA Ticket Format."""
    
    def setUp(self):
        self.ticket = BATicketFormat(
            summary="Implement user authentication",
            description="Add OAuth 2.0 support",
            issue_type=IssueType.STORY,
            priority=Priority.HIGH
        )
    
    def test_add_business_value(self):
        """Test adding business value."""
        self.ticket.add_business_value("Improve user security")
        self.assertEqual(self.ticket.business_value, "Improve user security")
    
    def test_add_assumptions(self):
        """Test adding assumptions."""
        self.ticket.add_assumption("OAuth provider is available")
        self.ticket.add_assumption("Users have email addresses")
        
        self.assertEqual(len(self.ticket.assumptions), 2)
    
    def test_add_non_functional_requirements(self):
        """Test adding non-functional requirements."""
        self.ticket.add_non_functional_requirement("Response time < 500ms")
        self.ticket.add_non_functional_requirement("99.9% uptime")
        
        self.assertEqual(len(self.ticket.non_functional_requirements), 2)
    
    def test_add_acceptance_criteria(self):
        """Test adding acceptance criteria."""
        self.ticket.add_acceptance_criterion("User can login with OAuth")
        self.ticket.add_acceptance_criterion("Session persists across requests")
        
        self.assertEqual(len(self.ticket.acceptance_criteria), 2)
    
    def test_to_jira_payload(self):
        """Test conversion to Jira payload."""
        self.ticket.add_business_value("Improve security")
        self.ticket.add_assumption("OAuth provider available")
        self.ticket.add_acceptance_criterion("User can login")
        
        payload = self.ticket.to_jira_payload("GREC")
        
        self.assertEqual(payload["fields"]["project"]["key"], "GREC")
        self.assertEqual(payload["fields"]["summary"], "Implement user authentication")
        self.assertEqual(payload["fields"]["issuetype"]["name"], "Story")
        self.assertIn("Business Value", payload["fields"]["description"])


class TestRESTClient(unittest.TestCase):
    """Test REST Client."""
    
    def setUp(self):
        self.client = RESTClient("https://api.example.com")
    
    @patch('shared.rest_client.requests.Session.request')
    def test_get_request(self, mock_request):
        """Test GET request."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 1, "name": "Test"}
        mock_request.return_value = mock_response
        
        result = self.client.get("/users/1")
        
        self.assertEqual(result["id"], 1)
        self.assertEqual(result["name"], "Test")
    
    @patch('shared.rest_client.requests.Session.request')
    def test_post_request(self, mock_request):
        """Test POST request."""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 1, "created": True}
        mock_request.return_value = mock_response
        
        result = self.client.post("/users", {"name": "Test"})
        
        self.assertEqual(result["id"], 1)
        self.assertTrue(result["created"])
    
    def test_request_history(self):
        """Test request history tracking."""
        self.assertEqual(len(self.client.request_history), 0)
        
        # History is populated during actual requests
        # This test verifies the history structure
        self.client.clear_history()
        self.assertEqual(len(self.client.request_history), 0)


class TestIntegrationOrchestrator(unittest.TestCase):
    """Test Integration Orchestrator."""
    
    def setUp(self):
        self.orchestrator = IntegrationOrchestrator()
    
    def test_register_rest_client(self):
        """Test registering a REST client."""
        self.orchestrator.register_rest_client(
            "external_api",
            "https://api.external.com"
        )
        
        client = self.orchestrator.get_rest_client("external_api")
        self.assertIsNotNone(client)
        self.assertEqual(client.base_url, "https://api.external.com")
    
    def test_get_integration_status(self):
        """Test getting integration status."""
        self.orchestrator.register_rest_client(
            "test_api",
            "https://api.test.com"
        )
        
        status = self.orchestrator.get_integration_status()
        
        self.assertIn("jira", status)
        self.assertIn("rest_clients", status)
        self.assertIn("test_api", status["rest_clients"])
    
    @patch('shared.jira_integration.JiraIntegrationService.create_ticket')
    def test_create_jira_ticket(self, mock_create):
        """Test creating a Jira ticket."""
        mock_create.return_value = {
            "success": True,
            "ticket_key": "GREC-123",
            "ticket_id": "10000",
            "url": "https://jira.example.com/browse/GREC-123"
        }
        
        response = self.orchestrator.create_jira_ticket(
            summary="Test ticket",
            description="Test description"
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.to_dict()["success"])


if __name__ == "__main__":
    unittest.main()

