"""
CourtListener API Tool
Integrates with CourtListener API to get case law summaries and court rulings
"""

import requests
import logging
from typing import Dict, Any, Optional, List
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CourtListenerAPI:
    """Tool for accessing CourtListener legal data"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.base_url = "https://www.courtlistener.com/api/rest/v3"
        self.session = requests.Session()
        
        # Set up authentication if token provided
        if api_token:
            self.session.headers.update({
                "Authorization": f"Token {api_token}"
            })
        
        self.session.headers.update({
            "User-Agent": "PolicyNavigatorAgent/1.0",
            "Content-Type": "application/json"
        })
    
    def search_opinions(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search for court opinions
        
        Args:
            query: Search query
            limit: Maximum number of results
        """
        logger.info(f"Searching CourtListener for opinions: {query}")
        
        try:
            params = {
                "q": query,
                "order_by": "-date_filed",
                "page_size": limit
            }
            
            response = self.session.get(f"{self.base_url}/search/", params=params)
            
            # Handle rate limiting or authentication errors gracefully
            if response.status_code == 429:
                return {
                    "success": False,
                    "error": "Rate limited. Please try again later.",
                    "query": query,
                    "results": []
                }
            elif response.status_code == 401:
                return {
                    "success": False,
                    "error": "Authentication required for CourtListener API.",
                    "query": query,
                    "results": []
                }
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "query": query,
                    "total_results": data.get("count", 0),
                    "results": data.get("results", [])
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "query": query,
                    "results": []
                }
                
        except requests.RequestException as e:
            logger.error(f"Error searching CourtListener: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "results": []
            }
    
    def get_case_details(self, case_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific case
        
        Args:
            case_id: CourtListener case ID
        """
        logger.info(f"Getting case details for: {case_id}")
        
        try:
            response = self.session.get(f"{self.base_url}/opinions/{case_id}/")
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "case": response.json()
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "case_id": case_id
                }
                
        except requests.RequestException as e:
            logger.error(f"Error getting case details: {e}")
            return {
                "success": False,
                "error": str(e),
                "case_id": case_id
            }

class CourtListenerTool:
    """aiXplain-compatible tool for CourtListener API with mock data fallback"""
    
    def __init__(self, api_token: Optional[str] = None):
        self.api = CourtListenerAPI(api_token)
        
        # Mock data for demonstration when API is not available
        self.mock_cases = {
            "section 230": [
                {
                    "case_name": "Fair Housing Council v. Roommates.com",
                    "court": "9th Circuit Court of Appeals",
                    "date_filed": "2008-04-03",
                    "citation": "521 F.3d 1157",
                    "summary": "Court ruled that Section 230 immunity does not protect websites that require users to answer discriminatory questions, as this constitutes development of unlawful content rather than passive hosting.",
                    "outcome": "Plaintiff won - Section 230 immunity limited",
                    "key_holdings": [
                        "Section 230 does not protect active development of illegal content",
                        "Requiring discriminatory questionnaires exceeds passive hosting",
                        "Websites can lose immunity through content development activities"
                    ]
                },
                {
                    "case_name": "Zeran v. America Online",
                    "court": "4th Circuit Court of Appeals", 
                    "date_filed": "1997-11-12",
                    "citation": "129 F.3d 327",
                    "summary": "Landmark case establishing broad interpretation of Section 230 immunity for ISPs. Court held that AOL could not be held liable for defamatory third-party content even after being notified.",
                    "outcome": "Defendant won - Broad Section 230 immunity",
                    "key_holdings": [
                        "Section 230 provides broad immunity for ISPs",
                        "No duty to remove content after notification",
                        "Publisher liability distinction eliminated for interactive services"
                    ]
                }
            ],
            "digital assets": [
                {
                    "case_name": "SEC v. Ripple Labs",
                    "court": "Southern District of New York",
                    "date_filed": "2020-12-22",
                    "citation": "Ongoing litigation",
                    "summary": "SEC alleges that Ripple's XRP token sales constituted unregistered securities offerings. Case has significant implications for cryptocurrency regulation.",
                    "outcome": "Ongoing - Mixed rulings on different aspects",
                    "key_holdings": [
                        "Institutional sales of XRP may constitute securities",
                        "Programmatic sales to retail investors may not be securities",
                        "Fair notice defense partially successful"
                    ]
                }
            ]
        }
    
    def search_case_law(self, regulation_or_topic: str) -> str:
        """
        Search for case law related to a regulation or legal topic
        
        Args:
            regulation_or_topic: The regulation name or legal topic to search for
        """
        logger.info(f"Searching case law for: {regulation_or_topic}")
        
        # First try the real API
        api_results = self.api.search_opinions(regulation_or_topic, limit=5)
        
        if api_results["success"] and api_results["results"]:
            return self._format_api_results(regulation_or_topic, api_results["results"])
        
        # Fall back to mock data for demonstration
        return self._format_mock_results(regulation_or_topic)
    
    def _format_api_results(self, query: str, results: List[Dict]) -> str:
        """Format real API results"""
        if not results:
            return f"No case law found for '{query}' in CourtListener database."
        
        output = f"**Case Law Search Results for '{query}':**\n\n"
        output += f"Found {len(results)} relevant cases:\n\n"
        
        for i, case in enumerate(results, 1):
            case_name = case.get("caseName", "Unknown Case")
            court = case.get("court", "Unknown Court")
            date_filed = case.get("dateFiled", "Unknown Date")
            citation = case.get("citation", "No citation available")
            
            output += f"{i}. **{case_name}**\n"
            output += f"   Court: {court}\n"
            output += f"   Date Filed: {date_filed}\n"
            output += f"   Citation: {citation}\n"
            
            if case.get("snippet"):
                snippet = case["snippet"][:300] + "..." if len(case["snippet"]) > 300 else case["snippet"]
                output += f"   Summary: {snippet}\n"
            
            output += "\n"
        
        return output
    
    def _format_mock_results(self, query: str) -> str:
        """Format mock results for demonstration"""
        # Check if we have mock data for this query
        relevant_cases = []
        query_lower = query.lower()
        
        for topic, cases in self.mock_cases.items():
            if topic in query_lower or any(word in query_lower for word in topic.split()):
                relevant_cases.extend(cases)
        
        if not relevant_cases:
            return f"""**Case Law Search for '{query}':**

No specific case law found in our demonstration database for this query. 

Note: This is a demo version with limited case law data. In a production environment, this would search the full CourtListener database with comprehensive legal opinions and court rulings.

Available demo topics include: Section 230, digital assets/cryptocurrency."""
        
        output = f"**Case Law Analysis for '{query}':**\n\n"
        output += f"Found {len(relevant_cases)} relevant case(s):\n\n"
        
        for i, case in enumerate(relevant_cases, 1):
            output += f"{i}. **{case['case_name']}**\n"
            output += f"   Court: {case['court']}\n"
            output += f"   Date Filed: {case['date_filed']}\n"
            output += f"   Citation: {case['citation']}\n"
            output += f"   Outcome: {case['outcome']}\n\n"
            
            output += f"   **Summary:** {case['summary']}\n\n"
            
            if case.get('key_holdings'):
                output += f"   **Key Holdings:**\n"
                for holding in case['key_holdings']:
                    output += f"   • {holding}\n"
                output += "\n"
        
        output += "---\n"
        output += "*Note: This demo includes selected landmark cases. Production version would provide comprehensive case law search.*"
        
        return output
    
    def get_case_summary(self, case_name: str) -> str:
        """
        Get a summary of a specific case
        
        Args:
            case_name: Name of the case to look up
        """
        logger.info(f"Getting case summary for: {case_name}")
        
        # Search through mock data first
        case_name_lower = case_name.lower()
        
        for topic, cases in self.mock_cases.items():
            for case in cases:
                if case_name_lower in case['case_name'].lower():
                    output = f"**Case Summary: {case['case_name']}**\n\n"
                    output += f"**Court:** {case['court']}\n"
                    output += f"**Date Filed:** {case['date_filed']}\n"
                    output += f"**Citation:** {case['citation']}\n"
                    output += f"**Outcome:** {case['outcome']}\n\n"
                    output += f"**Summary:**\n{case['summary']}\n\n"
                    
                    if case.get('key_holdings'):
                        output += f"**Key Legal Holdings:**\n"
                        for holding in case['key_holdings']:
                            output += f"• {holding}\n"
                    
                    return output
        
        return f"Case '{case_name}' not found in demonstration database. In production, this would search the full CourtListener database."

if __name__ == "__main__":
    # Test the CourtListener tool
    tool = CourtListenerTool()
    
    # Test Section 230 search
    print("Testing Section 230 case law search:")
    result = tool.search_case_law("Section 230")
    print(result)
    
    print("\n" + "="*50 + "\n")
    
    # Test specific case lookup
    print("Testing specific case lookup:")
    case_summary = tool.get_case_summary("Fair Housing Council v. Roommates.com")
    print(case_summary)