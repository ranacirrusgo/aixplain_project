"""
Policy Navigator Agent CLI Interface
Command-line interface for interacting with the Policy Navigator Agent
"""

import click
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.policy_navigator_agent import PolicyNavigatorAgent
from tools.slack_integration import SlackTool

# Load environment variables
load_dotenv()

@click.group()
@click.version_option(version="1.0.0", prog_name="Policy Navigator Agent")
def cli():
    """Policy Navigator Agent - Multi-Agent RAG System for Government Regulation Search"""
    pass

@cli.command()
@click.option('--initialize-data', is_flag=True, default=True, 
              help='Initialize knowledge base with policy documents')
def setup(initialize_data):
    """Set up the Policy Navigator Agent and initialize the knowledge base"""
    click.echo("🚀 Setting up Policy Navigator Agent...")
    
    try:
        agent = PolicyNavigatorAgent(initialize_data=initialize_data)
        
        # Test components
        click.echo("\n🔧 Testing components...")
        test_results = agent.test_components()
        
        for component, status in test_results.items():
            status_icon = "✅" if status else "❌"
            click.echo(f"{status_icon} {component.replace('_', ' ').title()}: {'PASS' if status else 'FAIL'}")
        
        # Show knowledge base stats
        stats = agent.get_knowledge_base_stats()
        click.echo(f"\n📚 Knowledge Base: {stats.get('document_count', 0)} documents indexed")
        
        click.echo("\n✅ Setup complete! Use 'policy-navigator query' to start asking questions.")
        
    except Exception as e:
        click.echo(f"❌ Setup failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('question', required=True)
@click.option('--save-history', is_flag=True, help='Save conversation to history file')
@click.option('--format', type=click.Choice(['text', 'json']), default='text', 
              help='Output format')
def query(question, save_history, format):
    """Ask a question to the Policy Navigator Agent"""
    click.echo(f"🤖 Policy Navigator Agent")
    click.echo(f"Query: {question}\n")
    
    try:
        # Initialize agent
        agent = PolicyNavigatorAgent(initialize_data=False)
        
        # Process query
        with click.progressbar(length=100, label='Processing query') as bar:
            response = agent.query(question)
            bar.update(100)
        
        if format == 'json':
            result = {
                "query": question,
                "response": response,
                "timestamp": agent._get_timestamp()
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("📋 Response:")
            click.echo("-" * 50)
            click.echo(response)
        
        # Save history if requested
        if save_history:
            history_file = Path("conversation_history.json")
            history = agent.get_conversation_history()
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            click.echo(f"\n💾 Conversation saved to {history_file}")
            
    except Exception as e:
        click.echo(f"❌ Query failed: {e}", err=True)
        sys.exit(1)

@cli.command()
def interactive():
    """Start an interactive session with the Policy Navigator Agent"""
    click.echo("🤖 Policy Navigator Agent - Interactive Mode")
    click.echo("Type 'exit' or 'quit' to end the session\n")
    
    try:
        agent = PolicyNavigatorAgent(initialize_data=False)
        
        while True:
            try:
                question = click.prompt("You", type=str)
                
                if question.lower() in ['exit', 'quit', 'bye']:
                    click.echo("👋 Goodbye!")
                    break
                
                if question.lower() in ['help', '?']:
                    click.echo("""
Available commands:
- Ask any policy or regulation question
- 'status': Check agent status
- 'stats': Show knowledge base statistics  
- 'history': Show conversation history
- 'clear': Clear conversation history
- 'help' or '?': Show this help
- 'exit' or 'quit': End session
                    """)
                    continue
                
                if question.lower() == 'status':
                    test_results = agent.test_components()
                    click.echo("Component Status:")
                    for component, status in test_results.items():
                        status_icon = "✅" if status else "❌"
                        click.echo(f"  {status_icon} {component.replace('_', ' ').title()}")
                    continue
                
                if question.lower() == 'stats':
                    stats = agent.get_knowledge_base_stats()
                    click.echo(f"Knowledge Base: {stats.get('document_count', 0)} documents")
                    click.echo(f"Embedding Model: {stats.get('embedding_model', 'Unknown')}")
                    continue
                
                if question.lower() == 'history':
                    history = agent.get_conversation_history()
                    click.echo(f"Conversation History ({len(history)} messages):")
                    for msg in history[-10:]:  # Show last 10 messages
                        role = msg['type'].capitalize()
                        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                        click.echo(f"  {role}: {content}")
                    continue
                
                if question.lower() == 'clear':
                    agent.clear_conversation_history()
                    click.echo("🗑️ Conversation history cleared")
                    continue
                
                # Process regular query
                response = agent.query(question)
                click.echo(f"\n🤖 Agent: {response}\n")
                
            except KeyboardInterrupt:
                click.echo("\n👋 Goodbye!")
                break
            except Exception as e:
                click.echo(f"❌ Error: {e}")
                
    except Exception as e:
        click.echo(f"❌ Failed to start interactive session: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--channel', help='Slack channel to send notification')
@click.option('--policy-title', required=True, help='Title of the policy')
@click.option('--update-type', required=True, 
              type=click.Choice(['New', 'Amendment', 'Repeal', 'Reminder']),
              help='Type of policy update')
@click.option('--details', required=True, help='Details of the update')
def notify(channel, policy_title, update_type, details):
    """Send a policy update notification via Slack"""
    click.echo("📢 Sending policy notification...")
    
    try:
        slack_tool = SlackTool()
        result = slack_tool.notify_policy_update(
            policy_title=policy_title,
            update_type=update_type,
            details=details,
            channel=channel
        )
        click.echo(result)
        
    except Exception as e:
        click.echo(f"❌ Notification failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--requirement', required=True, help='Compliance requirement description')
@click.option('--deadline', required=True, help='Deadline date (YYYY-MM-DD)')
@click.option('--channel', help='Slack channel for reminder')
def remind(requirement, deadline, channel):
    """Set a compliance deadline reminder"""
    click.echo("⏰ Setting compliance reminder...")
    
    try:
        slack_tool = SlackTool()
        result = slack_tool.set_compliance_reminder(
            requirement=requirement,
            deadline_date=deadline,
            channel=channel
        )
        click.echo(result)
        
    except Exception as e:
        click.echo(f"❌ Reminder failed: {e}", err=True)
        sys.exit(1)

@cli.command()
def status():
    """Check the status of all agent components"""
    click.echo("🔍 Checking Policy Navigator Agent status...")
    
    try:
        agent = PolicyNavigatorAgent(initialize_data=False)
        test_results = agent.test_components()
        
        click.echo("\nComponent Status:")
        all_passing = True
        for component, status in test_results.items():
            status_icon = "✅" if status else "❌"
            status_text = "PASS" if status else "FAIL"
            click.echo(f"{status_icon} {component.replace('_', ' ').title()}: {status_text}")
            if not status:
                all_passing = False
        
        # Knowledge base stats
        stats = agent.get_knowledge_base_stats()
        click.echo(f"\n📚 Knowledge Base:")
        click.echo(f"  Documents: {stats.get('document_count', 0)}")
        click.echo(f"  Model: {stats.get('embedding_model', 'Unknown')}")
        
        if all_passing:
            click.echo("\n✅ All systems operational!")
        else:
            click.echo("\n⚠️ Some components need attention")
            
    except Exception as e:
        click.echo(f"❌ Status check failed: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--format', type=click.Choice(['json', 'csv', 'text']), default='text',
              help='Export format')
@click.option('--output', help='Output file path')
def export_history(format, output):
    """Export conversation history"""
    try:
        agent = PolicyNavigatorAgent(initialize_data=False)
        history = agent.get_conversation_history()
        
        if not history:
            click.echo("No conversation history found")
            return
        
        if not output:
            output = f"conversation_history.{format}"
        
        if format == 'json':
            with open(output, 'w') as f:
                json.dump(history, f, indent=2)
        elif format == 'csv':
            import pandas as pd
            df = pd.DataFrame(history)
            df.to_csv(output, index=False)
        else:  # text
            with open(output, 'w') as f:
                for msg in history:
                    f.write(f"{msg['timestamp']} - {msg['type'].upper()}: {msg['content']}\n\n")
        
        click.echo(f"✅ History exported to {output}")
        
    except Exception as e:
        click.echo(f"❌ Export failed: {e}", err=True)

# Example queries for help
EXAMPLE_QUERIES = [
    "Is Executive Order 14067 still in effect?",
    "What are the compliance requirements for GDPR?",
    "Has Section 230 ever been challenged in court?",
    "Show me recent regulations from the EPA",
    "Analyze compliance requirements for digital assets"
]

@cli.command()
def examples():
    """Show example queries you can try"""
    click.echo("📝 Example queries you can try:\n")
    
    for i, query in enumerate(EXAMPLE_QUERIES, 1):
        click.echo(f"{i}. {query}")
    
    click.echo(f"\nTry: policy-navigator query \"Is Executive Order 14067 still in effect?\"")


@cli.command()
@click.option('--policy-title', required=True, help='Title of the policy')
@click.option('--update-type', required=True, 
              type=click.Choice(['New', 'Amendment', 'Repeal', 'Reminder']),
              help='Type of policy update')
@click.option('--details', required=True, help='Details of the update')
@click.option('--database-id', help='Notion database ID (optional)')
def notion(policy_title, update_type, details, database_id):
    """Create a policy entry in Notion database"""
    if not NOTION_AVAILABLE:
        click.echo("❌ Notion integration not available. Install: pip install notion-client")
        return
    
    click.echo("📝 Creating Notion entry...")
    
    try:
        notion_tool = NotionTool()
        result = notion_tool.create_policy_entry(
            policy_title=policy_title,
            update_type=update_type,
            details=details,
            database_id=database_id
        )
        click.echo(result)
        
    except Exception as e:
        click.echo(f"❌ Notion operation failed: {e}", err=True)
# Add this import after the existing ones
try:
    from tools.notion_integration import NotionTool
    NOTION_AVAILABLE = True
except ImportError:
    NOTION_AVAILABLE = False
    click.echo("⚠️ Notion integration not available. Install: pip install notion-client")


if __name__ == '__main__':
    cli()