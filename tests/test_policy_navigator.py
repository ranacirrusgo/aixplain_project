"""
Unit tests for Policy Navigator Agent
"""

import unittest
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.data_ingestion import DataIngestionManager
from src.vector_store import VectorStoreManager
from src.policy_navigator_agent import PolicyNavigatorAgent
from tools.federal_register_api import FederalRegisterTool
from tools.courtlistener_api import CourtListenerTool
from tools.custom_analysis_tool import CustomPolicyTool

class TestDataIngestion(unittest.TestCase):
    """Test data ingestion components"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_manager = DataIngestionManager(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_download_policy_dataset(self):
        """Test policy dataset creation"""
        dataset_path = self.data_manager.download_policy_dataset()
        self.assertTrue(os.path.exists(dataset_path))
        
        # Check if file contains expected data
        import json
        with open(dataset_path, 'r') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("id", data[0])
        self.assertIn("title", data[0])
        self.assertIn("text", data[0])
    
    def test_scrape_epa_website(self):
        """Test EPA website scraping (mock data)"""
        scraped_path = self.data_manager.scrape_epa_website()
        self.assertTrue(os.path.exists(scraped_path))
        
        import json
        with open(scraped_path, 'r') as f:
            data = json.load(f)
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
    
    def test_process_documents(self):
        """Test document processing"""
        # First create the raw data
        self.data_manager.download_policy_dataset()
        self.data_manager.scrape_epa_website()
        
        # Process documents
        docs = self.data_manager.process_documents()
        
        self.assertIsInstance(docs, list)
        self.assertGreater(len(docs), 0)
        
        # Check document structure
        doc = docs[0]
        self.assertIn("id", doc)
        self.assertIn("title", doc)
        self.assertIn("content", doc)
        self.assertIn("metadata", doc)

class TestVectorStore(unittest.TestCase):
    """Test vector store functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store = VectorStoreManager(self.temp_dir)
        
        # Create test documents
        self.test_docs = [
            {
                "id": "test-1",
                "title": "Test Policy 1",
                "content": "This is a test policy about data protection and privacy regulations.",
                "metadata": {"type": "test", "date": "2024-01-01"}
            },
            {
                "id": "test-2", 
                "title": "Test Policy 2",
                "content": "This policy covers financial regulations and compliance requirements.",
                "metadata": {"type": "test", "date": "2024-01-02"}
            }
        ]
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_add_documents(self):
        """Test adding documents to vector store"""
        self.vector_store.add_documents(self.test_docs)
        
        # Check collection stats
        stats = self.vector_store.get_collection_stats()
        self.assertEqual(stats["document_count"], len(self.test_docs))
    
    def test_search_documents(self):
        """Test document search functionality"""
        # Add documents first
        self.vector_store.add_documents(self.test_docs)
        
        # Search for relevant documents
        results = self.vector_store.search_documents("data protection privacy")
        
        self.assertIn("results", results)
        self.assertGreater(len(results["results"]), 0)
        
        # Check result structure
        result = results["results"][0]
        self.assertIn("id", result)
        self.assertIn("document", result)
        self.assertIn("metadata", result)
        self.assertIn("relevance_score", result)

class TestExternalAPIs(unittest.TestCase):
    """Test external API integrations"""
    
    def test_federal_register_tool(self):
        """Test Federal Register API tool"""
        tool = FederalRegisterTool()
        
        # Test status check
        result = tool.check_policy_status("Executive Order 14067")
        self.assertIsInstance(result, str)
        self.assertIn("Executive Order", result)
    
    def test_courtlistener_tool(self):
        """Test CourtListener API tool"""
        tool = CourtListenerTool()
        
        # Test case law search
        result = tool.search_case_law("Section 230")
        self.assertIsInstance(result, str)
        self.assertIn("case", result.lower())
    
    def test_custom_analysis_tool(self):
        """Test custom policy analysis tool"""
        tool = CustomPolicyTool()
        
        test_text = """
        Financial institutions must implement new procedures within 90 days.
        Companies shall not engage in prohibited activities.
        Violations may result in penalties up to $100,000.
        """
        
        # Test compliance analysis
        result = tool.analyze_policy_compliance(test_text, "Test Policy")
        self.assertIsInstance(result, str)
        self.assertIn("compliance", result.lower())
        self.assertIn("mandatory", result.lower())

class TestPolicyNavigatorAgent(unittest.TestCase):
    """Test main agent functionality"""
    
    def setUp(self):
        # Initialize agent without data to avoid long setup
        self.agent = PolicyNavigatorAgent(initialize_data=False)
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.data_manager)
        self.assertIsNotNone(self.agent.vector_store)
        self.assertIsNotNone(self.agent.federal_register_tool)
        self.assertIsNotNone(self.agent.courtlistener_tool)
        self.assertIsNotNone(self.agent.custom_analysis_tool)
    
    def test_component_testing(self):
        """Test component status checking"""
        test_results = self.agent.test_components()
        
        self.assertIsInstance(test_results, dict)
        self.assertIn("federal_register_api", test_results)
        self.assertIn("courtlistener_api", test_results)
        self.assertIn("custom_analysis", test_results)
    
    def test_query_processing(self):
        """Test query processing in standalone mode"""
        # Test a simple query
        response = self.agent.query("What is Executive Order 14067?")
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        # Check conversation history
        history = self.agent.get_conversation_history()
        self.assertGreater(len(history), 0)
        
        # Check that both user query and response are recorded
        self.assertEqual(history[-2]["type"], "user")
        self.assertEqual(history[-1]["type"], "assistant")

class TestCLIInterface(unittest.TestCase):
    """Test CLI interface"""
    
    def test_cli_imports(self):
        """Test that CLI module imports successfully"""
        try:
            import cli
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"CLI import failed: {e}")

def run_tests():
    """Run all tests"""
    unittest.main(verbosity=2)

if __name__ == "__main__":
    run_tests()