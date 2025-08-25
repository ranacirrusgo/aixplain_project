"""
Policy Navigator Agent - Main Agent Implementation
Multi-Agent RAG System for Government Regulation Search using aiXplain SDK
"""

import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import json

# Import our custom components
from .data_ingestion import DataIngestionManager
from .vector_store import VectorStoreManager, VectorSearchTool

# Import tools with absolute imports when run as script
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from tools.federal_register_api import FederalRegisterTool
from tools.courtlistener_api import CourtListenerTool
from tools.custom_analysis_tool import CustomPolicyTool

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    # Check for API key first
    api_key = os.getenv("AIXPLAIN_API_KEY") or os.getenv("TEAM_API_KEY")
    if api_key:
        os.environ["TEAM_API_KEY"] = api_key  # Set the key that aiXplain expects
        import aixplain
        from aixplain.factories import AgentFactory, ToolFactory
        from aixplain.enums import Function
        AIXPLAIN_AVAILABLE = True
        logger.info("aiXplain SDK loaded successfully")
    else:
        AIXPLAIN_AVAILABLE = False
        logger.warning("aiXplain API key not found in environment variables")
except (ImportError, Exception) as e:
    AIXPLAIN_AVAILABLE = False
    logger.warning(f"aiXplain SDK not available: {e}")

class PolicyNavigatorAgent:
    """Main Policy Navigator Agent Class"""
    
    def __init__(self, initialize_data: bool = True):
        """
        Initialize the Policy Navigator Agent
        
        Args:
            initialize_data: Whether to initialize data ingestion and vector store
        """
        logger.info("Initializing Policy Navigator Agent...")
        
        # Initialize components
        self.data_manager = DataIngestionManager()
        self.vector_store = VectorStoreManager()
        self.vector_search_tool = VectorSearchTool(self.vector_store)
        
        # Initialize external API tools
        self.federal_register_tool = FederalRegisterTool()
        self.courtlistener_tool = CourtListenerTool()
        self.custom_analysis_tool = CustomPolicyTool()
        
        # Agent state
        self.agent = None
        self.tools = {}
        self.conversation_history = []
        
        # Initialize data if requested
        if initialize_data:
            self._initialize_knowledge_base()
        
        # Setup aiXplain agent if available
        if AIXPLAIN_AVAILABLE:
            self._setup_aixplain_agent()
        else:
            logger.warning("Running in standalone mode without aiXplain integration")
    
    def _initialize_knowledge_base(self):
        """Initialize the knowledge base with policy documents"""
        logger.info("Initializing knowledge base...")
        
        # Check if we already have data
        stats = self.vector_store.get_collection_stats()
        if stats.get("document_count", 0) > 0:
            logger.info(f"Knowledge base already contains {stats['document_count']} documents")
            return
        
        # Ingest and index documents
        documents = self.data_manager.ingest_all_data()
        if documents:
            self.vector_store.add_documents(documents)
            logger.info(f"Knowledge base initialized with {len(documents)} documents")
        else:
            logger.warning("No documents ingested")
    
    def _setup_aixplain_agent(self):
        """Setup the aiXplain agent with tools"""
        try:
            api_key = os.getenv("AIXPLAIN_API_KEY")
            if not api_key:
                logger.warning("AIXPLAIN_API_KEY not found in environment variables")
                return
            
            # Set the API key
            aixplain.api_key = api_key
            
            # Create custom tools for aiXplain
            self._create_aixplain_tools()
            
            # Create the agent
            self.agent = AgentFactory.create(
                name="Policy Navigator Agent",
                description="An intelligent agent for navigating government policies and regulations",
                instructions="""You are a Policy Navigator Agent specialized in helping users understand and navigate complex government regulations, compliance policies, and public health guidelines.

Your capabilities include:
1. Searching policy documents and regulations
2. Checking real-time policy status via Federal Register
3. Finding relevant case law and court rulings
4. Analyzing compliance requirements
5. Providing regulatory updates and notifications

Always provide accurate, well-sourced information with proper citations. When uncertain, clearly state the limitations and suggest consulting official sources or legal counsel.""",
                tools=list(self.tools.values())
            )
            
            logger.info("aiXplain agent created successfully")
            
        except Exception as e:
            logger.error(f"Error setting up aiXplain agent: {e}")
            self.agent = None
    
    def _create_aixplain_tools(self):
        """Create aiXplain-compatible tools"""
        try:
            # Policy Document Search Tool
            search_tool = ToolFactory.create_function_tool(
                name="search_policy_documents",
                description="Search through policy and regulation documents using vector similarity",
                parameters={
                    "query": {
                        "type": "string",
                        "description": "Search query for policy documents"
                    },
                    "num_results": {
                        "type": "integer", 
                        "description": "Number of results to return (default: 3)",
                        "default": 3
                    }
                },
                function=self.vector_search_tool.search_policy_documents
            )
            self.tools["search_policy_documents"] = search_tool
            
            # Federal Register Status Check Tool
            status_tool = ToolFactory.create_function_tool(
                name="check_policy_status",
                description="Check the current status of policies and executive orders via Federal Register API",
                parameters={
                    "policy_identifier": {
                        "type": "string",
                        "description": "Policy name, executive order number, or document identifier"
                    }
                },
                function=self.federal_register_tool.check_policy_status
            )
            self.tools["check_policy_status"] = status_tool
            
            # Case Law Search Tool
            case_law_tool = ToolFactory.create_function_tool(
                name="search_case_law",
                description="Search for case law and court rulings related to regulations",
                parameters={
                    "regulation_or_topic": {
                        "type": "string",
                        "description": "Regulation name or legal topic to search for"
                    }
                },
                function=self.courtlistener_tool.search_case_law
            )
            self.tools["search_case_law"] = case_law_tool
            
            # Compliance Analysis Tool
            compliance_tool = ToolFactory.create_function_tool(
                name="analyze_compliance_requirements",
                description="Analyze policy documents for compliance requirements and obligations",
                parameters={
                    "document_text": {
                        "type": "string",
                        "description": "Full text of the policy document to analyze"
                    },
                    "document_title": {
                        "type": "string",
                        "description": "Title of the document (optional)",
                        "default": ""
                    }
                },
                function=self.custom_analysis_tool.analyze_policy_compliance
            )
            self.tools["analyze_compliance_requirements"] = compliance_tool
            
            logger.info(f"Created {len(self.tools)} aiXplain tools")
            
        except Exception as e:
            logger.error(f"Error creating aiXplain tools: {e}")
            self.tools = {}
    
    def query(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a user query and return a response
        
        Args:
            user_query: The user's question or request
            context: Optional context information
        """
        logger.info(f"Processing query: {user_query}")
        
        # Add to conversation history
        self.conversation_history.append({
            "type": "user",
            "content": user_query,
            "timestamp": self._get_timestamp()
        })
        
        try:
            if self.agent and AIXPLAIN_AVAILABLE:
                # Use aiXplain agent
                response = self._query_aixplain_agent(user_query, context)
            else:
                # Use standalone processing
                response = self._query_standalone(user_query, context)
            
            # Add response to history
            self.conversation_history.append({
                "type": "assistant", 
                "content": response,
                "timestamp": self._get_timestamp()
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            error_response = f"I apologize, but I encountered an error while processing your query: {str(e)}. Please try rephrasing your question or contact support if the issue persists."
            return error_response
    
    def _query_aixplain_agent(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process query using aiXplain agent"""
        try:
            # Run the agent
            result = self.agent.run(user_query)
            
            if hasattr(result, 'data') and hasattr(result.data, 'output'):
                return result.data.output
            else:
                return str(result)
                
        except Exception as e:
            logger.error(f"Error with aiXplain agent: {e}")
            # Fallback to standalone mode
            return self._query_standalone(user_query, context)
    
    def _query_standalone(self, user_query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process query in standalone mode without aiXplain"""
        logger.info("Processing query in standalone mode")
        
        response = "**Policy Navigator Agent Response:**\n\n"
        
        # Determine query type and route accordingly
        query_lower = user_query.lower()
        
        # Check if it's a status check query
        if any(keyword in query_lower for keyword in ["status", "effect", "active", "repealed", "executive order"]):
            logger.info("Routing to policy status check")
            status_result = self.federal_register_tool.check_policy_status(user_query)
            response += status_result + "\n\n"
        
        # Check if it's a case law query
        if any(keyword in query_lower for keyword in ["case law", "court", "ruling", "challenge", "lawsuit"]):
            logger.info("Routing to case law search")
            case_result = self.courtlistener_tool.search_case_law(user_query)
            response += case_result + "\n\n"
        
        # Always search our policy documents
        logger.info("Searching policy documents")
        search_result = self.vector_search_tool.search_policy_documents(user_query, 3)
        response += "**Relevant Policy Documents:**\n" + search_result + "\n\n"
        
        # Add helpful context
        response += "---\n*This response was generated using the Policy Navigator Agent. For official legal advice, please consult with qualified legal counsel.*"
        
        return response
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        return self.vector_store.get_collection_stats()
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return self.conversation_history
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def test_components(self) -> Dict[str, Any]:
        """Test all components and return status"""
        test_results = {
            "data_ingestion": False,
            "vector_store": False,
            "federal_register_api": False,
            "courtlistener_api": False,
            "custom_analysis": False,
            "aixplain_agent": False
        }
        
        try:
            # Test data ingestion
            stats = self.vector_store.get_collection_stats()
            test_results["data_ingestion"] = stats.get("document_count", 0) > 0
            test_results["vector_store"] = True
            
            # Test Federal Register API
            fr_result = self.federal_register_tool.check_policy_status("Executive Order 14067")
            test_results["federal_register_api"] = "Executive Order" in fr_result
            
            # Test CourtListener API
            cl_result = self.courtlistener_tool.search_case_law("Section 230")
            test_results["courtlistener_api"] = "case" in cl_result.lower()
            
            # Test custom analysis
            ca_result = self.custom_analysis_tool.analyze_policy_compliance(
                "Companies must comply within 30 days.", "Test Policy"
            )
            test_results["custom_analysis"] = "compliance" in ca_result.lower()
            
            # Test aiXplain agent
            test_results["aixplain_agent"] = self.agent is not None
            
        except Exception as e:
            logger.error(f"Error testing components: {e}")
        
        return test_results

if __name__ == "__main__":
    # Test the agent
    agent = PolicyNavigatorAgent()
    
    # Test components
    print("Testing Policy Navigator Agent components...")
    test_results = agent.test_components()
    for component, status in test_results.items():
        print(f"✓ {component}: {'PASS' if status else 'FAIL'}")
    
    print("\n" + "="*50 + "\n")
    
    # Test queries
    test_queries = [
        "Is Executive Order 14067 still in effect?",
        "Has Section 230 ever been challenged in court?",
        "What are the compliance requirements for digital assets?"
    ]
    
    for query in test_queries:
        print(f"Query: {query}")
        response = agent.query(query)
        print(f"Response: {response[:200]}...")
        print("\n" + "-"*30 + "\n")