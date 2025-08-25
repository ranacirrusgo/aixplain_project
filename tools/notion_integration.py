"""
Notion Integration Tool
Provides Notion database integration for policy tracking and management
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from notion_client import Client
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotionTool:
    """Notion integration for policy management"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                self.client = Client(auth=self.api_key)
                logger.info("Notion client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Notion client: {e}")
        else:
            logger.warning("Notion API key not found")
    
    def create_policy_entry(self, policy_title: str, update_type: str, 
                          details: str, database_id: Optional[str] = None) -> str:
        """Create a new policy entry in Notion database"""
        if not self.client:
            return "❌ Notion client not initialized"
        
        # Use default database ID if not provided
        db_id = database_id or os.getenv("NOTION_DATABASE_ID")
        if not db_id:
            return "❌ Notion database ID not configured"
        
        try:
            properties = {
                "Policy Title": {"title": [{"text": {"content": policy_title}}]},
                "Update Type": {"select": {"name": update_type}},
                "Details": {"rich_text": [{"text": {"content": details}}]},
                "Date": {"date": {"start": datetime.now().isoformat()}}
            }
            
            response = self.client.pages.create(
                parent={"database_id": db_id},
                properties=properties
            )
            
            return f"✅ Policy entry created in Notion: {policy_title}"
            
        except Exception as e:
            return f"❌ Failed to create Notion entry: {str(e)}"
    
    def test_connection(self) -> str:
        """Test Notion connection"""
        if not self.client:
            return "❌ Notion client not initialized"
        
        try:
            users = self.client.users.list()
            return f"✅ Notion connection successful! Found {len(users['results'])} users"
        except Exception as e:
            return f"❌ Notion connection failed: {str(e)}"
