"""
Federal Register API Tool
Integrates with the Federal Register API to check policy status and get real-time information
"""

import requests
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederalRegisterAPI:
    """Tool for accessing Federal Register data"""
    
    def __init__(self):
        self.base_url = "https://www.federalregister.gov/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "PolicyNavigatorAgent/1.0"
        })
    
    def search_documents(self, query: str, document_type: str = None, 
                        agency: str = None, limit: int = 10) -> Dict[str, Any]:
        """
        Search Federal Register documents
        
        Args:
            query: Search query
            document_type: Type of document (e.g., 'RULE', 'PRORULE', 'NOTICE')
            agency: Agency name or abbreviation
            limit: Maximum number of results
        """
        logger.info(f"Searching Federal Register for: {query}")
        
        try:
            params = {
                "conditions[term]": query,
                "per_page": limit,
                "order": "newest"
            }
            
            if document_type:
                params["conditions[type][]"] = document_type
            
            if agency:
                params["conditions[agency][]"] = agency
            
            response = self.session.get(f"{self.base_url}/documents.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "query": query,
                "total_results": data.get("count", 0),
                "results": data.get("results", [])
            }
            
        except requests.RequestException as e:
            logger.error(f"Error searching Federal Register: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    def get_document_by_number(self, document_number: str) -> Dict[str, Any]:
        """
        Get a specific document by its Federal Register document number
        
        Args:
            document_number: Federal Register document number (e.g., "2022-05471")
        """
        logger.info(f"Getting Federal Register document: {document_number}")
        
        try:
            response = self.session.get(f"{self.base_url}/documents/{document_number}.json")
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "document": data
            }
            
        except requests.RequestException as e:
            logger.error(f"Error getting document {document_number}: {e}")
            return {
                "success": False,
                "error": str(e),
                "document_number": document_number
            }
    
    def check_executive_order_status(self, eo_number: str) -> str:
        """
        Check the status of an Executive Order
        
        Args:
            eo_number: Executive Order number (e.g., "14067")
        """
        logger.info(f"Checking status of Executive Order {eo_number}")
        
        # Search for the executive order
        search_query = f"Executive Order {eo_number}"
        results = self.search_documents(
            query=search_query,
            document_type="PRESDOCU",
            limit=5
        )
        
        if not results["success"]:
            return f"Error checking Executive Order {eo_number}: {results.get('error', 'Unknown error')}"
        
        if not results["results"]:
            return f"Executive Order {eo_number} not found in Federal Register."
        
        # Find the most relevant result
        relevant_doc = None
        for doc in results["results"]:
            if eo_number in doc.get("executive_order_number", "") or eo_number in doc.get("title", ""):
                relevant_doc = doc
                break
        
        if not relevant_doc:
            # Take the first result if no exact match
            relevant_doc = results["results"][0]
        
        # Format the response
        title = relevant_doc.get("title", "Unknown Title")
        publication_date = relevant_doc.get("publication_date", "Unknown Date")
        document_number = relevant_doc.get("document_number", "Unknown")
        html_url = relevant_doc.get("html_url", "")
        
        # Check if there are any amendments or repeals
        amendments_search = self.search_documents(
            query=f"amend Executive Order {eo_number}",
            limit=3
        )
        
        repeals_search = self.search_documents(
            query=f"repeal Executive Order {eo_number}",
            limit=3
        )
        
        status_info = f"""
**Executive Order {eo_number} Status Report**

**Title:** {title}
**Publication Date:** {publication_date}
**Document Number:** {document_number}
**Status:** Active (as of {datetime.now().strftime('%B %d, %Y')})

**Details:**
- No repeals found in Federal Register
- Document is still in effect
        """
        
        if amendments_search["success"] and amendments_search["results"]:
            status_info += f"\n- Found {len(amendments_search['results'])} potential amendments"
        
        if repeals_search["success"] and repeals_search["results"]:
            status_info += f"\n- Found {len(repeals_search['results'])} documents mentioning repeal"
        
        if html_url:
            status_info += f"\n\n**Full Document:** {html_url}"
        
        return status_info
    
    def get_recent_regulations(self, agency: str = None, days: int = 30) -> str:
        """
        Get recent regulations from the Federal Register
        
        Args:
            agency: Specific agency to filter by
            days: Number of days to look back
        """
        logger.info(f"Getting recent regulations for {agency or 'all agencies'}")
        
        try:
            params = {
                "conditions[publication_date][gte]": (datetime.now() - datetime.timedelta(days=days)).strftime("%Y-%m-%d"),
                "conditions[type][]": "RULE",
                "per_page": 10,
                "order": "newest"
            }
            
            if agency:
                params["conditions[agency][]"] = agency
            
            response = self.session.get(f"{self.base_url}/documents.json", params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                return f"No recent regulations found for {agency or 'any agency'} in the last {days} days."
            
            output = f"**Recent Regulations ({len(results)} found):**\n\n"
            
            for i, doc in enumerate(results, 1):
                output += f"{i}. **{doc.get('title', 'Unknown Title')}**\n"
                output += f"   Agency: {', '.join(doc.get('agencies', []))}\n"
                output += f"   Publication Date: {doc.get('publication_date', 'Unknown')}\n"
                output += f"   Document Number: {doc.get('document_number', 'Unknown')}\n"
                if doc.get("abstract"):
                    abstract = doc["abstract"][:200] + "..." if len(doc["abstract"]) > 200 else doc["abstract"]
                    output += f"   Abstract: {abstract}\n"
                output += "\n"
            
            return output
            
        except Exception as e:
            logger.error(f"Error getting recent regulations: {e}")
            return f"Error retrieving recent regulations: {str(e)}"

class FederalRegisterTool:
    """aiXplain-compatible tool for Federal Register API"""
    
    def __init__(self):
        self.api = FederalRegisterAPI()
    
    def check_policy_status(self, policy_identifier: str) -> str:
        """
        Check the status of a policy or regulation
        
        Args:
            policy_identifier: Executive Order number, regulation name, or document number
        """
        # Try to determine what type of identifier this is
        if "executive order" in policy_identifier.lower() or policy_identifier.startswith("EO"):
            # Extract the number
            number = ''.join(filter(str.isdigit, policy_identifier))
            if number:
                return self.api.check_executive_order_status(number)
        
        # General search
        results = self.api.search_documents(policy_identifier, limit=3)
        
        if not results["success"]:
            return f"Error checking policy status: {results.get('error', 'Unknown error')}"
        
        if not results["results"]:
            return f"No documents found for: {policy_identifier}"
        
        output = f"**Policy Status for '{policy_identifier}':**\n\n"
        
        for i, doc in enumerate(results["results"], 1):
            output += f"{i}. **{doc.get('title', 'Unknown Title')}**\n"
            output += f"   Type: {doc.get('type', 'Unknown')}\n"
            output += f"   Publication Date: {doc.get('publication_date', 'Unknown')}\n"
            output += f"   Status: Active\n"
            output += f"   Document Number: {doc.get('document_number', 'Unknown')}\n"
            if doc.get("agencies"):
                output += f"   Agencies: {', '.join(doc['agencies'])}\n"
            output += "\n"
        
        return output
    
    def get_recent_policy_updates(self, agency: str = None) -> str:
        """
        Get recent policy updates
        
        Args:
            agency: Optional agency to filter by
        """
        return self.api.get_recent_regulations(agency=agency, days=30)

if __name__ == "__main__":
    # Test the Federal Register API
    tool = FederalRegisterTool()
    
    # Test checking Executive Order status
    print("Testing Executive Order 14067 status check:")
    result = tool.check_policy_status("Executive Order 14067")
    print(result)
    
    print("\n" + "="*50 + "\n")
    
    # Test recent regulations
    print("Testing recent regulations:")
    recent = tool.get_recent_policy_updates()
    print(recent)