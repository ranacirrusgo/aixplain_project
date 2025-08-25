"""
Slack Integration Tool
Provides Slack notifications and updates for policy changes and reminders
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SlackIntegration:
    """Slack integration for policy notifications and updates"""
    
    def __init__(self, bot_token: Optional[str] = None):
        self.bot_token = bot_token or os.getenv("SLACK_BOT_TOKEN")
        self.base_url = "https://slack.com/api"
        
        if not self.bot_token:
            logger.warning("Slack bot token not provided. Some features will not be available.")
        
        self.session = requests.Session()
        if self.bot_token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.bot_token}",
                "Content-Type": "application/json"
            })
    
    def send_message(self, channel: str, text: str, blocks: Optional[List[Dict]] = None) -> Dict[str, Any]:
        """
        Send a message to a Slack channel
        
        Args:
            channel: Channel ID or name (e.g., "#general" or "C1234567890")
            text: Message text
            blocks: Optional Slack blocks for rich formatting
        """
        if not self.bot_token:
            logger.warning("Cannot send Slack message: bot token not configured")
            return {"ok": False, "error": "no_bot_token"}
        
        logger.info(f"Sending Slack message to {channel}")
        
        try:
            payload = {
                "channel": channel,
                "text": text
            }
            
            if blocks:
                payload["blocks"] = blocks
            
            response = self.session.post(f"{self.base_url}/chat.postMessage", json=payload)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error sending Slack message: {e}")
            return {"ok": False, "error": str(e)}
    
    def send_policy_update(self, channel: str, policy_title: str, update_type: str, 
                          details: str, url: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a formatted policy update notification
        
        Args:
            channel: Slack channel
            policy_title: Title of the policy
            update_type: Type of update (e.g., "New", "Amendment", "Repeal")
            details: Update details
            url: Optional URL to the policy document
        """
        # Determine emoji based on update type
        emoji_map = {
            "new": "🆕",
            "amendment": "📝", 
            "repeal": "❌",
            "reminder": "⏰",
            "deadline": "🚨"
        }
        emoji = emoji_map.get(update_type.lower(), "📋")
        
        # Create rich message blocks
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Policy Update: {update_type}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{policy_title}*\n\n{details}"
                }
            }
        ]
        
        if url:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{url}|View Full Document>"
                }
            })
        
        # Add footer
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Policy Navigator Agent • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                }
            ]
        })
        
        text = f"{emoji} Policy Update: {policy_title} - {update_type}"
        return self.send_message(channel, text, blocks)
    
    def send_compliance_reminder(self, channel: str, requirement: str, 
                               deadline: str, days_remaining: int) -> Dict[str, Any]:
        """
        Send a compliance deadline reminder
        
        Args:
            channel: Slack channel
            requirement: Compliance requirement description
            deadline: Deadline date
            days_remaining: Number of days until deadline
        """
        # Determine urgency level
        if days_remaining <= 7:
            color = "danger"
            emoji = "🚨"
            urgency = "URGENT"
        elif days_remaining <= 30:
            color = "warning"
            emoji = "⚠️"
            urgency = "Important"
        else:
            color = "good"
            emoji = "📅"
            urgency = "Upcoming"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} {urgency} Compliance Reminder"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Requirement:* {requirement}\n*Deadline:* {deadline}\n*Days Remaining:* {days_remaining}"
                }
            }
        ]
        
        if days_remaining <= 7:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ *This deadline is approaching soon. Please take immediate action.*"
                }
            })
        
        text = f"{emoji} Compliance Reminder: {requirement} - {days_remaining} days remaining"
        return self.send_message(channel, text, blocks)
    
    def send_query_response(self, channel: str, user_query: str, response: str) -> Dict[str, Any]:
        """
        Send a formatted response to a user query
        
        Args:
            channel: Slack channel or user DM
            user_query: Original user query
            response: Agent response
        """
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Query:* {user_query}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": response[:3000]  # Slack has message length limits
                }
            }
        ]
        
        if len(response) > 3000:
            blocks.append({
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "⚠️ Response truncated due to length. Please use the CLI for full response."
                    }
                ]
            })
        
        text = f"Policy Navigator Response to: {user_query[:100]}"
        return self.send_message(channel, text, blocks)
    
    def create_channel(self, channel_name: str, is_private: bool = False) -> Dict[str, Any]:
        """
        Create a new Slack channel
        
        Args:
            channel_name: Name of the channel to create
            is_private: Whether the channel should be private
        """
        if not self.bot_token:
            return {"ok": False, "error": "no_bot_token"}
        
        logger.info(f"Creating Slack channel: {channel_name}")
        
        try:
            endpoint = "conversations.create"
            payload = {
                "name": channel_name,
                "is_private": is_private
            }
            
            response = self.session.post(f"{self.base_url}/{endpoint}", json=payload)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error creating Slack channel: {e}")
            return {"ok": False, "error": str(e)}
    
    def schedule_reminder(self, channel: str, text: str, post_at: int) -> Dict[str, Any]:
        """
        Schedule a message to be sent later
        
        Args:
            channel: Slack channel
            text: Message text
            post_at: Unix timestamp when to post the message
        """
        if not self.bot_token:
            return {"ok": False, "error": "no_bot_token"}
        
        logger.info(f"Scheduling Slack reminder for {datetime.fromtimestamp(post_at)}")
        
        try:
            payload = {
                "channel": channel,
                "text": text,
                "post_at": post_at
            }
            
            response = self.session.post(f"{self.base_url}/chat.scheduleMessage", json=payload)
            return response.json()
            
        except Exception as e:
            logger.error(f"Error scheduling Slack message: {e}")
            return {"ok": False, "error": str(e)}

class SlackTool:
    """aiXplain-compatible tool for Slack integration"""
    
    def __init__(self, bot_token: Optional[str] = None):
        self.slack = SlackIntegration(bot_token)
        self.default_channel = os.getenv("SLACK_DEFAULT_CHANNEL", "#policy-updates")
    
    def notify_policy_update(self, policy_title: str, update_type: str, 
                           details: str, channel: Optional[str] = None) -> str:
        """
        Send a policy update notification to Slack
        
        Args:
            policy_title: Title of the policy
            update_type: Type of update
            details: Update details
            channel: Optional Slack channel (uses default if not provided)
        """
        target_channel = channel or self.default_channel
        
        result = self.slack.send_policy_update(
            channel=target_channel,
            policy_title=policy_title,
            update_type=update_type,
            details=details
        )
        
        if result.get("ok"):
            return f"✅ Policy update notification sent to {target_channel}"
        else:
            error = result.get("error", "Unknown error")
            return f"❌ Failed to send notification: {error}"
    
    def set_compliance_reminder(self, requirement: str, deadline_date: str, 
                              channel: Optional[str] = None) -> str:
        """
        Set a compliance deadline reminder
        
        Args:
            requirement: Compliance requirement description
            deadline_date: Deadline date (YYYY-MM-DD format)
            channel: Optional Slack channel
        """
        try:
            from datetime import datetime
            deadline = datetime.strptime(deadline_date, "%Y-%m-%d")
            days_remaining = (deadline - datetime.now()).days
            
            target_channel = channel or self.default_channel
            
            result = self.slack.send_compliance_reminder(
                channel=target_channel,
                requirement=requirement,
                deadline=deadline_date,
                days_remaining=days_remaining
            )
            
            if result.get("ok"):
                return f"✅ Compliance reminder set for {deadline_date} ({days_remaining} days remaining)"
            else:
                error = result.get("error", "Unknown error")
                return f"❌ Failed to set reminder: {error}"
                
        except ValueError:
            return "❌ Invalid date format. Please use YYYY-MM-DD format."
        except Exception as e:
            return f"❌ Error setting reminder: {str(e)}"
    
    def send_to_slack(self, message: str, channel: Optional[str] = None) -> str:
        """
        Send a general message to Slack
        
        Args:
            message: Message to send
            channel: Optional Slack channel
        """
        target_channel = channel or self.default_channel
        
        result = self.slack.send_message(target_channel, message)
        
        if result.get("ok"):
            return f"✅ Message sent to {target_channel}"
        else:
            error = result.get("error", "Unknown error")
            return f"❌ Failed to send message: {error}"

# Mock Slack functionality for demonstration
class MockSlackIntegration:
    """Mock Slack integration for testing and demonstration"""
    
    def __init__(self):
        self.sent_messages = []
        logger.info("Using mock Slack integration for demonstration")
    
    def send_policy_update(self, channel: str, policy_title: str, update_type: str, 
                          details: str, url: Optional[str] = None) -> Dict[str, Any]:
        """Mock policy update notification"""
        message = {
            "channel": channel,
            "type": "policy_update",
            "policy_title": policy_title,
            "update_type": update_type,
            "details": details,
            "url": url,
            "timestamp": datetime.now().isoformat()
        }
        self.sent_messages.append(message)
        
        logger.info(f"Mock Slack: Policy update sent to {channel}")
        return {"ok": True, "message": message}
    
    def send_compliance_reminder(self, channel: str, requirement: str, 
                               deadline: str, days_remaining: int) -> Dict[str, Any]:
        """Mock compliance reminder"""
        message = {
            "channel": channel,
            "type": "compliance_reminder", 
            "requirement": requirement,
            "deadline": deadline,
            "days_remaining": days_remaining,
            "timestamp": datetime.now().isoformat()
        }
        self.sent_messages.append(message)
        
        logger.info(f"Mock Slack: Compliance reminder sent to {channel}")
        return {"ok": True, "message": message}
    
    def get_sent_messages(self) -> List[Dict[str, Any]]:
        """Get all sent messages for testing"""
        return self.sent_messages

if __name__ == "__main__":
    # Test Slack integration
    slack_tool = SlackTool()
    
    # Test policy update notification
    print("Testing policy update notification:")
    result = slack_tool.notify_policy_update(
        policy_title="Executive Order 14067",
        update_type="Amendment",
        details="New provisions added for cryptocurrency regulation compliance."
    )
    print(result)
    
    print("\nTesting compliance reminder:")
    result = slack_tool.set_compliance_reminder(
        requirement="Implement new AML procedures",
        deadline_date="2024-06-01"
    )
    print(result)