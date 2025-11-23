"""
Jira Integration Service - Structured Jira ticket format with BA-specific fields.

Supports business value, assumptions, non-functional requirements, and other
BA-specific fields for comprehensive ticket creation and management.
"""

import logging
import requests
from typing import Dict, Any, Optional, List
from enum import Enum
from . import key_vault_client

logger = logging.getLogger(__name__)


class IssueType(Enum):
    """Jira issue types."""
    STORY = "Story"
    TASK = "Task"
    BUG = "Bug"
    EPIC = "Epic"
    SUBTASK = "Sub-task"
    FEATURE = "Feature"


class Priority(Enum):
    """Jira priority levels."""
    LOWEST = "Lowest"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    HIGHEST = "Highest"


class BATicketFormat:
    """
    Business Analysis specific ticket format.
    
    Includes fields for:
    - Business value
    - Assumptions
    - Non-functional requirements
    - Acceptance criteria
    - Dependencies
    - Stakeholders
    """
    
    def __init__(
        self,
        summary: str,
        description: str,
        issue_type: IssueType = IssueType.STORY,
        priority: Priority = Priority.MEDIUM
    ):
        self.summary = summary
        self.description = description
        self.issue_type = issue_type
        self.priority = priority
        
        # BA-specific fields
        self.business_value: Optional[str] = None
        self.assumptions: List[str] = []
        self.non_functional_requirements: List[str] = []
        self.acceptance_criteria: List[str] = []
        self.dependencies: List[str] = []
        self.stakeholders: List[str] = []
        self.estimated_effort: Optional[str] = None
        self.labels: List[str] = []
        self.epic_link: Optional[str] = None
    
    def add_business_value(self, value: str) -> "BATicketFormat":
        """Add business value statement."""
        self.business_value = value
        return self
    
    def add_assumption(self, assumption: str) -> "BATicketFormat":
        """Add an assumption."""
        self.assumptions.append(assumption)
        return self
    
    def add_non_functional_requirement(self, requirement: str) -> "BATicketFormat":
        """Add a non-functional requirement."""
        self.non_functional_requirements.append(requirement)
        return self
    
    def add_acceptance_criterion(self, criterion: str) -> "BATicketFormat":
        """Add an acceptance criterion."""
        self.acceptance_criteria.append(criterion)
        return self
    
    def add_dependency(self, dependency: str) -> "BATicketFormat":
        """Add a dependency."""
        self.dependencies.append(dependency)
        return self
    
    def add_stakeholder(self, stakeholder: str) -> "BATicketFormat":
        """Add a stakeholder."""
        self.stakeholders.append(stakeholder)
        return self
    
    def set_estimated_effort(self, effort: str) -> "BATicketFormat":
        """Set estimated effort (e.g., '5 points', '3 days')."""
        self.estimated_effort = effort
        return self
    
    def add_label(self, label: str) -> "BATicketFormat":
        """Add a label."""
        self.labels.append(label)
        return self
    
    def set_epic_link(self, epic_key: str) -> "BATicketFormat":
        """Link to an epic."""
        self.epic_link = epic_key
        return self
    
    def to_jira_payload(self, project_key: str) -> Dict[str, Any]:
        """Convert to Jira API payload."""
        description_parts = [self.description]
        
        if self.business_value:
            description_parts.append(f"\n*Business Value:*\n{self.business_value}")
        
        if self.assumptions:
            description_parts.append(f"\n*Assumptions:*\n" + "\n".join(f"- {a}" for a in self.assumptions))
        
        if self.non_functional_requirements:
            description_parts.append(f"\n*Non-Functional Requirements:*\n" + "\n".join(f"- {r}" for r in self.non_functional_requirements))
        
        if self.acceptance_criteria:
            description_parts.append(f"\n*Acceptance Criteria:*\n" + "\n".join(f"- {c}" for c in self.acceptance_criteria))
        
        if self.dependencies:
            description_parts.append(f"\n*Dependencies:*\n" + "\n".join(f"- {d}" for d in self.dependencies))
        
        if self.stakeholders:
            description_parts.append(f"\n*Stakeholders:*\n" + "\n".join(f"- {s}" for s in self.stakeholders))
        
        payload = {
            "fields": {
                "project": {"key": project_key},
                "summary": self.summary,
                "description": "".join(description_parts),
                "issuetype": {"name": self.issue_type.value},
                "priority": {"name": self.priority.value},
                "labels": self.labels
            }
        }
        
        if self.epic_link:
            payload["fields"]["customfield_10000"] = self.epic_link
        
        return payload


class JiraIntegrationService:
    """
    Jira integration service with BA-specific ticket support.
    
    Provides:
    - Ticket creation with BA fields
    - Ticket updates
    - Issue search
    - Transition management
    """
    
    def __init__(self):
        self.base_url = None
        self.api_token = None
        self.project_key = "GREC"
        self._load_config()
    
    def _load_config(self) -> None:
        """Load Jira configuration from environment/vault."""
        import os
        self.base_url = os.environ.get("JIRA_BASE_URL", "https://jira.example.com")
        secret_name = os.environ.get("JIRA_API_TOKEN_SECRET", "jira-api-token")
        try:
            self.api_token = key_vault_client.get_secret(secret_name)
        except Exception as e:
            logger.warning(f"Could not load Jira API token: {e}")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_ticket(self, ticket: BATicketFormat) -> Dict[str, Any]:
        """
        Create a Jira ticket with BA-specific fields.
        
        Returns:
            {
                "success": bool,
                "ticket_key": str,
                "ticket_id": str,
                "url": str,
                "error": str (if failed)
            }
        """
        try:
            payload = ticket.to_jira_payload(self.project_key)
            url = f"{self.base_url}/rest/api/3/issues"
            
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            
            result = response.json()
            ticket_key = result.get("key")
            ticket_id = result.get("id")
            
            logger.info(f"Created Jira ticket: {ticket_key}")
            
            return {
                "success": True,
                "ticket_key": ticket_key,
                "ticket_id": ticket_id,
                "url": f"{self.base_url}/browse/{ticket_key}"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating Jira ticket: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_ticket(self, ticket_key: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Jira ticket."""
        try:
            url = f"{self.base_url}/rest/api/3/issues/{ticket_key}"
            payload = {"fields": updates}
            
            response = requests.put(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            
            logger.info(f"Updated Jira ticket: {ticket_key}")
            
            return {"success": True, "ticket_key": ticket_key}
        except requests.exceptions.RequestException as e:
            logger.error(f"Error updating Jira ticket: {e}")
            return {"success": False, "error": str(e)}
    
    def search_tickets(self, jql: str) -> Dict[str, Any]:
        """Search Jira tickets using JQL."""
        try:
            url = f"{self.base_url}/rest/api/3/search"
            params = {"jql": jql, "maxResults": 50}
            
            response = requests.get(url, params=params, headers=self._get_headers())
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Jira: {e}")
            return {"issues": [], "error": str(e)}

