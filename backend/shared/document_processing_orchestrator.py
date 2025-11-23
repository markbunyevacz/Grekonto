"""
Document Processing Intelligence - Integration Architecture and Orchestration.

Complete orchestration system for:
1. Document ingestion and preprocessing
2. Intelligent classification and routing
3. Structured content extraction
4. AI-powered acceptance criteria detection
5. Automated ticket generation and workflow integration
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

from .document_parser import (
    DocumentParser, DocumentAnalyzer, get_document_parser, get_document_analyzer,
    AnalysisResult, StructuredContent
)
from .document_classifier import DocumentClassifier, get_document_classifier
from .acceptance_criteria_detector import (
    AcceptanceCriteriaDetector, get_acceptance_criteria_detector, Ticket
)

logger = logging.getLogger(__name__)


@dataclass
class ProcessingPipeline:
    """Configuration for document processing pipeline."""
    enable_classification: bool = True
    enable_analysis: bool = True
    enable_criteria_detection: bool = True
    enable_ticket_generation: bool = True
    auto_routing: bool = True
    min_confidence: float = 0.6


@dataclass
class ProcessingResult:
    """Complete result of document processing."""
    document_id: str
    classification_result: Optional[Dict] = None
    structured_content: Optional[StructuredContent] = None
    analysis_result: Optional[AnalysisResult] = None
    generated_tickets: List[Ticket] = None
    routing_decision: Optional[Dict] = None
    processing_status: str = "SUCCESS"
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "document_id": self.document_id,
            "classification": self.classification_result,
            "structured_content": self.structured_content.to_dict() if self.structured_content else None,
            "analysis": self.analysis_result.to_dict() if self.analysis_result else None,
            "tickets": [t.to_dict() for t in (self.generated_tickets or [])],
            "routing_decision": self.routing_decision,
            "status": self.processing_status,
            "error": self.error_message,
            "processing_time_ms": self.processing_time_ms,
        }


class DocumentProcessingOrchestrator:
    """
    Complete orchestration of document processing pipeline.
    
    Coordinates:
    1. Document classification (intelligent routing)
    2. Structured content extraction (hierarchy preservation)
    3. AI-powered analysis (acceptance criteria detection)
    4. Ticket generation (automated workflow)
    """
    
    def __init__(self, pipeline_config: Optional[ProcessingPipeline] = None):
        """
        Initialize orchestrator.
        
        Args:
            pipeline_config: Optional pipeline configuration
        """
        self.config = pipeline_config or ProcessingPipeline()
        
        # Initialize components
        self.parser = get_document_parser()
        self.analyzer = get_document_analyzer()
        self.classifier = get_document_classifier()
        self.detector = get_acceptance_criteria_detector()
        
        logger.info("DocumentProcessingOrchestrator initialized")
    
    def process_document(self, document_text: str, document_id: str,
                        document_format: str = "text",
                        document_type_hint: Optional[str] = None,
                        process_config: Optional[ProcessingPipeline] = None) -> ProcessingResult:
        """
        Process document through complete pipeline.
        
        Args:
            document_text: Full document text
            document_id: Unique document identifier
            document_format: Document format (text, markdown, html, etc.)
            document_type_hint: Optional hint about document type
            process_config: Optional per-request pipeline config
            
        Returns:
            ProcessingResult with all stages completed
        """
        import time
        
        start_time = time.time()
        config = process_config or self.config
        
        logger.info(f"Starting document processing: {document_id}")
        
        result = ProcessingResult(
            document_id=document_id,
            generated_tickets=[]
        )
        
        try:
            # Stage 1: Classification and Routing
            if config.enable_classification:
                logger.info("Stage 1: Classification")
                classification_result = self.classifier.classify(document_text, document_type_hint)
                
                result.classification_result = {
                    "primary_category": classification_result.primary_category,
                    "confidence_score": classification_result.confidence_score,
                    "secondary_categories": [
                        {"category": cat, "score": score}
                        for cat, score in classification_result.secondary_categories
                    ],
                    "routing_rules": classification_result.routing_rules_triggered,
                    "keywords": classification_result.keywords_matched,
                }
                
                # Check confidence threshold
                if classification_result.confidence_score < config.min_confidence:
                    logger.warning(f"Low confidence classification: "
                                  f"{classification_result.confidence_score:.2%}")
                
                # Determine routing
                if config.auto_routing:
                    result.routing_decision = {
                        "category": classification_result.primary_category,
                        "confidence": classification_result.confidence_score,
                        "routes": classification_result.routing_rules_triggered,
                    }
            
            # Stage 2: Structured Content Extraction
            if config.enable_analysis:
                logger.info("Stage 2: Content Extraction")
                structured = self.parser.extract_structured_content(
                    document_text, document_format
                )
                result.structured_content = structured
            
            # Stage 3: AI-Powered Analysis
            if config.enable_analysis:
                logger.info("Stage 3: AI Analysis")
                analysis_result = self.analyzer.analyze_document(
                    document_text, document_id, document_format
                )
                result.analysis_result = analysis_result
            
            # Stage 4: Ticket Generation
            if config.enable_ticket_generation and result.analysis_result:
                logger.info("Stage 4: Ticket Generation")
                
                # Extract acceptance criteria
                criteria = result.analysis_result.detected_acceptance_criteria
                
                # Generate tickets
                tickets = self.detector.generate_tickets_from_criteria(
                    [{"type": "BDD", "given": c.title, "when": c.description, 
                      "then": "; ".join(c.acceptance_tests)}
                     for c in criteria],
                    document_id
                )
                
                # Link dependencies
                tickets = self.detector.link_ticket_dependencies(tickets)
                
                result.generated_tickets = tickets
                logger.info(f"Generated {len(tickets)} tickets")
            
            result.processing_status = "SUCCESS"
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}", exc_info=True)
            result.processing_status = "ERROR"
            result.error_message = str(e)
        
        finally:
            result.processing_time_ms = (time.time() - start_time) * 1000
        
        logger.info(f"Document processing complete: {document_id} "
                   f"({result.processing_time_ms:.0f}ms)")
        
        return result
    
    def batch_process_documents(self, documents: List[Dict[str, str]]) -> List[ProcessingResult]:
        """
        Process multiple documents.
        
        Args:
            documents: List of dicts with 'text', 'id', and optional 'format', 'type_hint'
            
        Returns:
            List of ProcessingResult objects
        """
        results = []
        
        for doc in documents:
            result = self.process_document(
                document_text=doc.get("text", ""),
                document_id=doc.get("id", f"doc_{len(results)}"),
                document_format=doc.get("format", "text"),
                document_type_hint=doc.get("type_hint"),
            )
            results.append(result)
        
        logger.info(f"Batch processing complete: {len(results)} documents")
        
        return results
    
    def route_document(self, classification_result: Dict,
                       processing_result: ProcessingResult) -> Dict[str, Any]:
        """
        Determine document routing based on classification and content.
        
        Args:
            classification_result: Classification results
            processing_result: Full processing results
            
        Returns:
            Routing decision with destination and actions
        """
        routing = {
            "destination": "default",
            "priority": "MEDIUM",
            "actions": [],
            "metadata": {}
        }
        
        category = classification_result.get("primary_category", "OTHER")
        confidence = classification_result.get("confidence_score", 0.0)
        
        # Route by category
        if category == "INVOICE":
            routing["destination"] = "invoice_processing"
            routing["priority"] = "HIGH" if confidence > 0.9 else "MEDIUM"
            routing["actions"] = ["validate_fields", "extract_amount", "match_vendor"]
        
        elif category == "SPECIFICATION":
            routing["destination"] = "requirement_analysis"
            routing["priority"] = "HIGH"
            
            if processing_result.analysis_result:
                ticket_count = len(processing_result.generated_tickets or [])
                if ticket_count > 0:
                    routing["actions"] = ["generate_tickets", "create_sprints"]
                    routing["metadata"]["ticket_count"] = ticket_count
        
        elif category == "CONTRACT":
            routing["destination"] = "legal_review"
            routing["priority"] = "CRITICAL"
            routing["actions"] = ["legal_review", "compliance_check"]
        
        elif category == "EMAIL":
            routing["destination"] = "email_processing"
            routing["priority"] = "MEDIUM"
            routing["actions"] = ["extract_attachments", "classify_priority"]
        
        else:
            routing["destination"] = "manual_review"
            routing["priority"] = "LOW"
        
        # Confidence-based routing
        if confidence < 0.6:
            routing["actions"].insert(0, "manual_review")
            routing["priority"] = "MEDIUM"
        
        return routing


class DocumentProcessingWorkflow:
    """
    Complete workflow for document processing with state management.
    
    Orchestrates:
    1. Ingestion
    2. Processing
    3. Output generation
    4. State tracking
    """
    
    def __init__(self):
        """Initialize workflow."""
        self.orchestrator = DocumentProcessingOrchestrator()
        self.processing_history = {}
    
    def ingest_and_process(self, document_text: str, document_id: str,
                          metadata: Optional[Dict] = None) -> ProcessingResult:
        """
        Complete workflow: ingest → process → output.
        
        Args:
            document_text: Document text
            document_id: Unique identifier
            metadata: Optional metadata
            
        Returns:
            Final processing result
        """
        logger.info(f"Workflow: Ingesting document {document_id}")
        
        # Ingest
        if not document_text or len(document_text) == 0:
            raise ValueError("Document text cannot be empty")
        
        # Detect format from content
        document_format = self._detect_format(document_text)
        
        # Process
        result = self.orchestrator.process_document(
            document_text=document_text,
            document_id=document_id,
            document_format=document_format,
        )
        
        # Store in history
        self.processing_history[document_id] = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": result.processing_status,
            "result": result
        }
        
        # Output formatting
        if result.processing_status == "SUCCESS":
            logger.info(f"Workflow complete: {document_id}")
        else:
            logger.error(f"Workflow failed: {document_id} - {result.error_message}")
        
        return result
    
    def _detect_format(self, text: str) -> str:
        """Detect document format from content."""
        if text.strip().startswith("```"):
            return "markdown"
        if text.strip().startswith("<"):
            return "html"
        if text.strip().startswith("{"):
            return "json"
        return "text"
    
    def get_processing_history(self, document_id: str) -> Optional[Dict]:
        """Get processing history for document."""
        return self.processing_history.get(document_id)
    
    def export_results(self, result: ProcessingResult,
                      format: str = "json") -> str:
        """Export processing results in specified format."""
        import json
        
        if format == "json":
            return json.dumps(result.to_dict(), indent=2)
        elif format == "markdown":
            return self._format_markdown(result)
        else:
            return str(result.to_dict())
    
    def _format_markdown(self, result: ProcessingResult) -> str:
        """Format results as markdown."""
        md = f"# Document Processing Report\n\n"
        md += f"**Document ID:** {result.document_id}\n"
        md += f"**Status:** {result.processing_status}\n"
        md += f"**Processing Time:** {result.processing_time_ms:.0f}ms\n\n"
        
        if result.classification_result:
            md += "## Classification\n"
            md += f"- **Category:** {result.classification_result['primary_category']}\n"
            md += f"- **Confidence:** {result.classification_result['confidence_score']:.1%}\n\n"
        
        if result.generated_tickets:
            md += "## Generated Tickets\n"
            for ticket in result.generated_tickets:
                md += f"- **{ticket.ticket_id}:** {ticket.title}\n"
                md += f"  - Priority: {ticket.priority}\n"
                md += f"  - Type: {ticket.type}\n"
        
        return md


# Global instances
_orchestrator: Optional[DocumentProcessingOrchestrator] = None
_workflow: Optional[DocumentProcessingWorkflow] = None


def get_orchestrator() -> DocumentProcessingOrchestrator:
    """Get or create global orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = DocumentProcessingOrchestrator()
    return _orchestrator


def get_workflow() -> DocumentProcessingWorkflow:
    """Get or create global workflow."""
    global _workflow
    if _workflow is None:
        _workflow = DocumentProcessingWorkflow()
    return _workflow
