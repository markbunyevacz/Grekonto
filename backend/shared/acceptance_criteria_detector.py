"""
Acceptance Criteria Detection and Ticket Generation Module.

Automated detection of acceptance criteria from documents and generation of actionable tickets:
- Structured acceptance criteria extraction
- Ticket generation with priorities and effort estimates
- Dependency tracking
- Automated ticket formatting for issue tracking systems
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


@dataclass
class Ticket:
    """Generated ticket from acceptance criteria."""
    ticket_id: str
    title: str
    description: str
    type: str  # story, task, bug, enhancement
    priority: str  # CRITICAL, HIGH, MEDIUM, LOW
    estimated_effort: Optional[str]
    acceptance_tests: List[str]
    dependencies: List[str]
    tags: List[str]
    status: str = "NEW"
    created_at: str = None
    due_date: Optional[str] = None
    assigned_to: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def to_jira_format(self) -> Dict:
        """Convert to Jira API format."""
        return {
            "fields": {
                "project": {"key": "GREC"},
                "summary": self.title,
                "description": self.description,
                "issuetype": {"name": self._map_type_to_jira()},
                "priority": {"name": self.priority},
                "labels": self.tags,
                "customfield_10000": self.estimated_effort,  # Custom field for effort
            }
        }
    
    def _map_type_to_jira(self) -> str:
        """Map ticket type to Jira issue type."""
        mapping = {
            "story": "Story",
            "task": "Task",
            "bug": "Bug",
            "enhancement": "Enhancement"
        }
        return mapping.get(self.type.lower(), "Task")
    
    def to_github_format(self) -> Dict:
        """Convert to GitHub Issues format."""
        labels = self.tags + [self.priority.lower(), self.type.lower()]
        
        return {
            "title": self.title,
            "body": self._format_github_body(),
            "labels": labels,
        }
    
    def _format_github_body(self) -> str:
        """Format ticket description for GitHub."""
        body = f"""## Description
{self.description}

## Acceptance Tests
"""
        for i, test in enumerate(self.acceptance_tests, 1):
            body += f"\n- [ ] {test}"
        
        if self.dependencies:
            body += "\n\n## Dependencies\n"
            for dep in self.dependencies:
                body += f"- {dep}\n"
        
        if self.estimated_effort:
            body += f"\n## Estimated Effort\n{self.estimated_effort}\n"
        
        return body


class AcceptanceCriteriaDetector:
    """
    Detects acceptance criteria from documents and generates tickets.
    
    Features:
    - BDD (Behavior-Driven Development) format parsing
    - User story format recognition
    - Automatic ticket generation
    - Dependency tracking
    - Integration with issue tracking systems
    """
    
    def __init__(self):
        """Initialize detector."""
        self.detected_criteria = []
        self.generated_tickets = []
    
    def extract_criteria_from_text(self, text: str) -> List[Dict]:
        """
        Extract acceptance criteria from plain text.
        
        Supports formats:
        - Given-When-Then (BDD)
        - "As a user, I want to..."
        - "Acceptance criteria:"
        - Numbered requirements
        """
        criteria_list = []
        
        # Split into potential criteria sections
        sections = self._split_into_sections(text)
        
        for section in sections:
            criterion = self._parse_criterion(section)
            if criterion:
                criteria_list.append(criterion)
        
        return criteria_list
    
    def _split_into_sections(self, text: str) -> List[str]:
        """Split text into potential acceptance criteria sections."""
        import re
        
        sections = []
        
        # Split by common criteria separators
        separators = [
            r'(?:Acceptance\s+Criteria|Acceptance\s+Test|Test\s+Case):\s*',
            r'(?:Given|When|Then|And|But)\s+',
            r'(?:As\s+a|I\s+want\s+to)\s+',
            r'\n\d+\.\s+',  # Numbered items
            r'\n[-•]\s+',   # Bullet points
        ]
        
        # Use aggressive splitting
        current_section = ""
        for line in text.split('\n'):
            line = line.strip()
            if line and any(re.match(sep, line) for sep in separators):
                if current_section:
                    sections.append(current_section)
                current_section = line
            elif current_section:
                current_section += " " + line
        
        if current_section:
            sections.append(current_section)
        
        return [s for s in sections if len(s) > 10]  # Filter very short sections
    
    def _parse_criterion(self, text: str) -> Optional[Dict]:
        """Parse single acceptance criterion."""
        import re
        
        if not text or len(text) < 10:
            return None
        
        criterion = {
            "original_text": text,
            "type": None,
            "given": None,
            "when": None,
            "then": None,
            "priority": "MEDIUM",
        }
        
        # BDD format
        given_match = re.search(r'(?:Given|GIVEN)\s+(.+?)(?=When|WHEN|When|$)', text, re.IGNORECASE | re.DOTALL)
        when_match = re.search(r'(?:When|WHEN)\s+(.+?)(?=Then|THEN|$)', text, re.IGNORECASE | re.DOTALL)
        then_match = re.search(r'(?:Then|THEN)\s+(.+?)$', text, re.IGNORECASE | re.DOTALL)
        
        if given_match or when_match or then_match:
            criterion["type"] = "BDD"
            if given_match:
                criterion["given"] = given_match.group(1).strip()
            if when_match:
                criterion["when"] = when_match.group(1).strip()
            if then_match:
                criterion["then"] = then_match.group(1).strip()
            return criterion
        
        # User story format
        story_match = re.search(r'As\s+a\s+(.+?),\s*I\s+want\s+to\s+(.+?)(?:\s+so\s+that\s+(.+?))?$', text, re.IGNORECASE)
        if story_match:
            criterion["type"] = "USER_STORY"
            criterion["actor"] = story_match.group(1)
            criterion["action"] = story_match.group(2)
            criterion["benefit"] = story_match.group(3)
            return criterion
        
        # Simple requirement
        criterion["type"] = "REQUIREMENT"
        return criterion
    
    def generate_tickets_from_criteria(self, criteria_list: List[Dict],
                                      document_id: str,
                                      project_prefix: str = "GREC") -> List[Ticket]:
        """
        Generate tickets from acceptance criteria.
        
        Args:
            criteria_list: List of extracted criteria
            document_id: Source document ID
            project_prefix: Project key for tickets
            
        Returns:
            List of generated tickets
        """
        tickets = []
        
        for i, criterion in enumerate(criteria_list, 1):
            ticket = self._create_ticket_from_criterion(
                criterion, i, document_id, project_prefix
            )
            if ticket:
                tickets.append(ticket)
        
        self.generated_tickets.extend(tickets)
        logger.info(f"Generated {len(tickets)} tickets from {len(criteria_list)} criteria")
        
        return tickets
    
    def _create_ticket_from_criterion(self, criterion: Dict, index: int,
                                     document_id: str,
                                     project_prefix: str) -> Optional[Ticket]:
        """Create a single ticket from criterion."""
        if criterion["type"] == "BDD":
            return self._create_bdd_ticket(criterion, index, document_id, project_prefix)
        elif criterion["type"] == "USER_STORY":
            return self._create_story_ticket(criterion, index, document_id, project_prefix)
        else:
            return self._create_requirement_ticket(criterion, index, document_id, project_prefix)
    
    def _create_bdd_ticket(self, criterion: Dict, index: int,
                          document_id: str, project_prefix: str) -> Ticket:
        """Create ticket from BDD criterion."""
        ticket_id = f"{project_prefix}-{1000 + index}"
        
        # Build title
        title = "BDD Scenario"
        if criterion.get("when"):
            title = criterion["when"][:80]
        
        # Build description
        description = "**Scenario:**\n"
        if criterion.get("given"):
            description += f"- Given: {criterion['given']}\n"
        if criterion.get("when"):
            description += f"- When: {criterion['when']}\n"
        if criterion.get("then"):
            description += f"- Then: {criterion['then']}\n"
        
        acceptance_tests = [
            f"Verify: {criterion.get('given', 'condition setup')}",
            f"Perform: {criterion.get('when', 'user action')}",
            f"Assert: {criterion.get('then', 'expected outcome')}",
        ]
        
        return Ticket(
            ticket_id=ticket_id,
            title=title,
            description=description,
            type="task",
            priority="MEDIUM",
            estimated_effort=None,
            acceptance_tests=acceptance_tests,
            dependencies=[],
            tags=["bdd", "automated-test", f"doc:{document_id[:8]}"],
        )
    
    def _create_story_ticket(self, criterion: Dict, index: int,
                            document_id: str, project_prefix: str) -> Ticket:
        """Create ticket from user story criterion."""
        ticket_id = f"{project_prefix}-{2000 + index}"
        
        actor = criterion.get("actor", "user")
        action = criterion.get("action", "perform action")
        benefit = criterion.get("benefit", "")
        
        title = f"As a {actor}, I want to {action}"[:80]
        
        description = f"""## User Story

**As a** {actor}  
**I want to** {action}
"""
        if benefit:
            description += f"**So that** {benefit}"
        
        acceptance_tests = [
            f"Verify {actor} can {action}",
            "Verify user interface is intuitive",
            "Verify no errors occur",
        ]
        
        return Ticket(
            ticket_id=ticket_id,
            title=title,
            description=description,
            type="story",
            priority="MEDIUM",
            estimated_effort="3-5 points",
            acceptance_tests=acceptance_tests,
            dependencies=[],
            tags=["story", "user-facing", f"doc:{document_id[:8]}"],
        )
    
    def _create_requirement_ticket(self, criterion: Dict, index: int,
                                  document_id: str, project_prefix: str) -> Ticket:
        """Create ticket from simple requirement."""
        ticket_id = f"{project_prefix}-{3000 + index}"
        
        text = criterion.get("original_text", "")[:100]
        
        return Ticket(
            ticket_id=ticket_id,
            title=text,
            description=criterion.get("original_text", ""),
            type="task",
            priority="MEDIUM",
            estimated_effort=None,
            acceptance_tests=[f"Verify: {text}"],
            dependencies=[],
            tags=["requirement", f"doc:{document_id[:8]}"],
        )
    
    def link_ticket_dependencies(self, tickets: List[Ticket]) -> List[Ticket]:
        """
        Automatically detect and link ticket dependencies.
        
        Args:
            tickets: List of tickets to analyze
            
        Returns:
            List of tickets with dependencies linked
        """
        import re
        
        for ticket in tickets:
            dependencies = []
            
            # Search for dependency keywords in description
            if re.search(r'depend|require|after|before|block', ticket.description, re.IGNORECASE):
                # Look for references to other tickets
                other_tickets = [t for t in tickets if t.ticket_id != ticket.ticket_id]
                
                for other_ticket in other_tickets:
                    # Simple matching logic
                    if re.search(re.escape(other_ticket.title[:20]), 
                               ticket.description, re.IGNORECASE):
                        dependencies.append(other_ticket.ticket_id)
            
            ticket.dependencies = dependencies
        
        return tickets
    
    def export_tickets_to_jira(self, tickets: List[Ticket]) -> List[Dict]:
        """Export tickets in Jira format."""
        return [ticket.to_jira_format() for ticket in tickets]
    
    def export_tickets_to_github(self, tickets: List[Ticket]) -> List[Dict]:
        """Export tickets in GitHub format."""
        return [ticket.to_github_format() for ticket in tickets]


def get_acceptance_criteria_detector() -> AcceptanceCriteriaDetector:
    """Get or create global detector."""
    return AcceptanceCriteriaDetector()
