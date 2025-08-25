"""
Demo Queries for Policy Navigator Agent
Demonstrates the capabilities of the agent with example queries and responses
"""

import sys
import os
from pathlib import Path
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.policy_navigator_agent import PolicyNavigatorAgent
from config.logging_config import setup_logging

def run_demo_queries():
    """Run a series of demo queries to showcase agent capabilities"""
    
    # Setup logging
    setup_logging("INFO")
    
    print("🤖 Policy Navigator Agent - Demo Session")
    print("=" * 60)
    print()
    
    # Initialize the agent
    print("🚀 Initializing Policy Navigator Agent...")
    agent = PolicyNavigatorAgent(initialize_data=True)
    
    # Check component status
    print("\n🔧 Component Status:")
    test_results = agent.test_components()
    for component, status in test_results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {component.replace('_', ' ').title()}")
    
    # Knowledge base stats
    stats = agent.get_knowledge_base_stats()
    print(f"\n📚 Knowledge Base: {stats.get('document_count', 0)} documents indexed")
    print()
    
    # Demo queries with expected capabilities
    demo_queries = [
        {
            "category": "Policy Status Check",
            "query": "Is Executive Order 14067 still in effect or has it been repealed?",
            "description": "Tests Federal Register API integration for real-time policy status"
        },
        {
            "category": "Case Law Research", 
            "query": "Has Section 230 ever been challenged in court? What was the outcome?",
            "description": "Tests CourtListener API integration for legal precedent research"
        },
        {
            "category": "Compliance Analysis",
            "query": "What are the compliance requirements for small businesses under GDPR?",
            "description": "Tests vector search and custom analysis tools for compliance guidance"
        },
        {
            "category": "Digital Assets Policy",
            "query": "What policies exist regarding cryptocurrency and digital assets regulation?",
            "description": "Tests comprehensive search across multiple policy documents"
        },
        {
            "category": "Environmental Regulations",
            "query": "What are the key requirements under the Clean Air Act?",
            "description": "Tests EPA data integration and policy document search"
        },
        {
            "category": "Data Protection",
            "query": "Compare HIPAA and GDPR privacy requirements",
            "description": "Tests policy comparison and analysis capabilities"
        }
    ]
    
    # Run demo queries
    for i, demo in enumerate(demo_queries, 1):
        print(f"📋 Demo Query {i}: {demo['category']}")
        print(f"Question: {demo['query']}")
        print(f"Purpose: {demo['description']}")
        print("-" * 60)
        
        # Measure response time
        start_time = time.time()
        response = agent.query(demo['query'])
        response_time = time.time() - start_time
        
        # Display response (truncated for readability)
        response_preview = response[:500] + "..." if len(response) > 500 else response
        print(f"Response ({response_time:.2f}s):")
        print(response_preview)
        print()
        print("=" * 60)
        print()
        
        # Small delay between queries
        time.sleep(1)
    
    # Show conversation history summary
    history = agent.get_conversation_history()
    print(f"📊 Session Summary:")
    print(f"  Total queries processed: {len([msg for msg in history if msg['type'] == 'user'])}")
    print(f"  Total responses generated: {len([msg for msg in history if msg['type'] == 'assistant'])}")
    print(f"  Average response length: {sum(len(msg['content']) for msg in history if msg['type'] == 'assistant') // len([msg for msg in history if msg['type'] == 'assistant']):.0f} characters")
    print()
    
    # Save conversation history
    import json
    history_file = Path(__file__).parent / "demo_conversation_history.json"
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)
    print(f"💾 Full conversation history saved to: {history_file}")
    
    print("\n🎉 Demo completed successfully!")
    print("Try the interactive mode: python cli.py interactive")

def demo_slack_integration():
    """Demo Slack integration capabilities"""
    print("\n📢 Slack Integration Demo")
    print("-" * 40)
    
    from tools.slack_integration import SlackTool
    
    slack_tool = SlackTool()
    
    # Test policy update notification
    print("Testing policy update notification...")
    result = slack_tool.notify_policy_update(
        policy_title="Executive Order 14067 - Digital Assets",
        update_type="Amendment",
        details="New implementation guidelines have been published for cryptocurrency compliance. Financial institutions must review and update their procedures by July 1, 2024."
    )
    print(f"Result: {result}")
    
    # Test compliance reminder
    print("\nTesting compliance reminder...")
    result = slack_tool.set_compliance_reminder(
        requirement="Update AML procedures for digital asset transactions",
        deadline_date="2024-07-01"
    )
    print(f"Result: {result}")

def demo_tool_capabilities():
    """Demonstrate individual tool capabilities"""
    print("\n🛠️ Individual Tool Demonstrations")
    print("=" * 50)
    
    # Federal Register API Demo
    print("\n1. Federal Register API Tool")
    print("-" * 30)
    from tools.federal_register_api import FederalRegisterTool
    
    fr_tool = FederalRegisterTool()
    result = fr_tool.check_policy_status("Executive Order 14067")
    print("Executive Order 14067 Status:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
    # CourtListener API Demo
    print("\n2. CourtListener API Tool")
    print("-" * 30)
    from tools.courtlistener_api import CourtListenerTool
    
    cl_tool = CourtListenerTool()
    result = cl_tool.search_case_law("Section 230")
    print("Section 230 Case Law:")
    print(result[:300] + "..." if len(result) > 300 else result)
    
    # Custom Analysis Tool Demo
    print("\n3. Custom Policy Analysis Tool")
    print("-" * 30)
    from tools.custom_analysis_tool import CustomPolicyTool
    
    ca_tool = CustomPolicyTool()
    sample_policy = """
    Financial institutions must implement comprehensive anti-money laundering (AML) procedures within 180 days of this regulation taking effect. 
    Institutions shall not process transactions exceeding $10,000 without proper documentation.
    Violations may result in penalties up to $500,000 per incident.
    Companies may voluntarily adopt enhanced due diligence measures for high-risk customers.
    """
    
    result = ca_tool.analyze_policy_compliance(sample_policy, "Sample AML Regulation")
    print("Compliance Analysis:")
    print(result[:400] + "..." if len(result) > 400 else result)
    
    # Vector Search Demo
    print("\n4. Vector Search Tool")
    print("-" * 30)
    from src.vector_store import VectorStoreManager, VectorSearchTool
    
    vector_store = VectorStoreManager()
    search_tool = VectorSearchTool(vector_store)
    result = search_tool.search_policy_documents("digital assets cryptocurrency regulation", 2)
    print("Vector Search Results:")
    print(result[:400] + "..." if len(result) > 400 else result)

if __name__ == "__main__":
    try:
        # Run main demo
        run_demo_queries()
        
        # Demo individual tools
        demo_tool_capabilities()
        
        # Demo Slack integration
        demo_slack_integration()
        
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()