"""
Custom Policy Analysis Tool
Provides advanced analysis capabilities for policy documents
"""

import re
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from collections import Counter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PolicyAnalysisTool:
    """Custom tool for advanced policy analysis"""
    
    def __init__(self):
        self.compliance_keywords = {
            "mandatory": ["must", "shall", "required", "mandatory", "obligated", "compelled"],
            "optional": ["may", "can", "could", "optional", "permitted", "allowed"],
            "prohibited": ["shall not", "must not", "cannot", "prohibited", "forbidden", "banned"],
            "timeframes": ["within", "by", "before", "after", "days", "months", "years", "immediately"],
            "penalties": ["penalty", "fine", "violation", "sanctions", "enforcement", "liability"]
        }
        
        self.compliance_patterns = {
            "deadline": r"within\s+(\d+)\s+(days?|months?|years?)",
            "percentage": r"(\d+(?:\.\d+)?)\s*%",
            "dollar_amount": r"\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)",
            "effective_date": r"effective\s+(on\s+)?(\w+\s+\d{1,2},?\s+\d{4})",
        }
    
    def analyze_compliance_requirements(self, document_text: str, document_title: str = "") -> str:
        """
        Analyze a policy document for compliance requirements
        
        Args:
            document_text: The full text of the policy document
            document_title: Optional title of the document
        """
        logger.info(f"Analyzing compliance requirements for: {document_title}")
        
        analysis = {
            "document_title": document_title,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "mandatory_requirements": [],
            "optional_provisions": [],
            "prohibited_actions": [],
            "deadlines": [],
            "penalties": [],
            "key_metrics": {}
        }
        
        # Analyze text by sentences
        sentences = self._split_into_sentences(document_text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Check for mandatory requirements
            if any(keyword in sentence_lower for keyword in self.compliance_keywords["mandatory"]):
                analysis["mandatory_requirements"].append(sentence.strip())
            
            # Check for optional provisions
            elif any(keyword in sentence_lower for keyword in self.compliance_keywords["optional"]):
                analysis["optional_provisions"].append(sentence.strip())
            
            # Check for prohibited actions
            elif any(keyword in sentence_lower for keyword in self.compliance_keywords["prohibited"]):
                analysis["prohibited_actions"].append(sentence.strip())
            
            # Check for deadlines
            deadline_match = re.search(self.compliance_patterns["deadline"], sentence_lower)
            if deadline_match:
                analysis["deadlines"].append({
                    "text": sentence.strip(),
                    "duration": f"{deadline_match.group(1)} {deadline_match.group(2)}"
                })
            
            # Check for penalties
            if any(keyword in sentence_lower for keyword in self.compliance_keywords["penalties"]):
                analysis["penalties"].append(sentence.strip())
        
        # Extract key metrics
        analysis["key_metrics"] = self._extract_metrics(document_text)
        
        return self._format_compliance_analysis(analysis)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting - could be improved with more sophisticated NLP
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_metrics(self, text: str) -> Dict[str, Any]:
        """Extract numerical metrics from text"""
        metrics = {}
        
        # Find percentages
        percentages = re.findall(self.compliance_patterns["percentage"], text)
        if percentages:
            metrics["percentages"] = [f"{p}%" for p in percentages]
        
        # Find dollar amounts
        dollar_amounts = re.findall(self.compliance_patterns["dollar_amount"], text)
        if dollar_amounts:
            metrics["dollar_amounts"] = [f"${amount}" for amount in dollar_amounts]
        
        # Find effective dates
        dates = re.findall(self.compliance_patterns["effective_date"], text, re.IGNORECASE)
        if dates:
            metrics["effective_dates"] = [date[1] for date in dates]
        
        return metrics
    
    def _format_compliance_analysis(self, analysis: Dict[str, Any]) -> str:
        """Format the compliance analysis into a readable report"""
        output = f"**Policy Compliance Analysis Report**\n"
        output += f"Document: {analysis['document_title'] or 'Untitled Document'}\n"
        output += f"Analysis Date: {analysis['analysis_date']}\n\n"
        
        # Mandatory Requirements
        if analysis["mandatory_requirements"]:
            output += f"**🔴 MANDATORY REQUIREMENTS ({len(analysis['mandatory_requirements'])}):**\n"
            for i, req in enumerate(analysis["mandatory_requirements"][:5], 1):  # Limit to top 5
                output += f"{i}. {req[:200]}{'...' if len(req) > 200 else ''}\n"
            if len(analysis["mandatory_requirements"]) > 5:
                output += f"... and {len(analysis['mandatory_requirements']) - 5} more\n"
            output += "\n"
        
        # Deadlines
        if analysis["deadlines"]:
            output += f"**⏰ CRITICAL DEADLINES ({len(analysis['deadlines'])}):**\n"
            for i, deadline in enumerate(analysis["deadlines"][:3], 1):
                output += f"{i}. {deadline['duration']} - {deadline['text'][:150]}{'...' if len(deadline['text']) > 150 else ''}\n"
            output += "\n"
        
        # Prohibited Actions
        if analysis["prohibited_actions"]:
            output += f"**🚫 PROHIBITED ACTIONS ({len(analysis['prohibited_actions'])}):**\n"
            for i, prohibition in enumerate(analysis["prohibited_actions"][:3], 1):
                output += f"{i}. {prohibition[:200]}{'...' if len(prohibition) > 200 else ''}\n"
            output += "\n"
        
        # Penalties
        if analysis["penalties"]:
            output += f"**⚖️ PENALTIES & ENFORCEMENT ({len(analysis['penalties'])}):**\n"
            for i, penalty in enumerate(analysis["penalties"][:3], 1):
                output += f"{i}. {penalty[:200]}{'...' if len(penalty) > 200 else ''}\n"
            output += "\n"
        
        # Optional Provisions
        if analysis["optional_provisions"]:
            output += f"**🟡 OPTIONAL PROVISIONS ({len(analysis['optional_provisions'])}):**\n"
            for i, provision in enumerate(analysis["optional_provisions"][:3], 1):
                output += f"{i}. {provision[:200]}{'...' if len(provision) > 200 else ''}\n"
            output += "\n"
        
        # Key Metrics
        if analysis["key_metrics"]:
            output += f"**📊 KEY METRICS:**\n"
            for metric_type, values in analysis["key_metrics"].items():
                if values:
                    output += f"- {metric_type.replace('_', ' ').title()}: {', '.join(values[:5])}\n"
            output += "\n"
        
        # Summary
        total_requirements = len(analysis["mandatory_requirements"])
        total_deadlines = len(analysis["deadlines"])
        total_penalties = len(analysis["penalties"])
        
        output += f"**📋 COMPLIANCE SUMMARY:**\n"
        output += f"- {total_requirements} mandatory requirements identified\n"
        output += f"- {total_deadlines} critical deadlines found\n"
        output += f"- {total_penalties} penalty provisions noted\n"
        
        if total_requirements > 0 or total_deadlines > 0:
            output += f"\n⚠️ **RECOMMENDATION:** Review all mandatory requirements and deadlines carefully. Consider creating a compliance checklist and calendar reminders for critical dates."
        
        return output
    
    def compare_policies(self, policy1_text: str, policy1_title: str, 
                        policy2_text: str, policy2_title: str) -> str:
        """
        Compare two policies and highlight differences
        
        Args:
            policy1_text: Text of first policy
            policy1_title: Title of first policy
            policy2_text: Text of second policy
            policy2_title: Title of second policy
        """
        logger.info(f"Comparing policies: {policy1_title} vs {policy2_title}")
        
        # Analyze both policies
        analysis1 = self._analyze_for_comparison(policy1_text)
        analysis2 = self._analyze_for_comparison(policy2_text)
        
        output = f"**Policy Comparison Report**\n"
        output += f"Policy A: {policy1_title}\n"
        output += f"Policy B: {policy2_title}\n"
        output += f"Comparison Date: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # Compare mandatory requirements
        common_reqs = set(analysis1["mandatory_keywords"]) & set(analysis2["mandatory_keywords"])
        unique_to_1 = set(analysis1["mandatory_keywords"]) - set(analysis2["mandatory_keywords"])
        unique_to_2 = set(analysis2["mandatory_keywords"]) - set(analysis1["mandatory_keywords"])
        
        output += f"**MANDATORY REQUIREMENTS COMPARISON:**\n"
        output += f"- Common requirements: {len(common_reqs)} ({', '.join(list(common_reqs)[:5])})\n"
        output += f"- Unique to {policy1_title}: {len(unique_to_1)} ({', '.join(list(unique_to_1)[:5])})\n"
        output += f"- Unique to {policy2_title}: {len(unique_to_2)} ({', '.join(list(unique_to_2)[:5])})\n\n"
        
        # Compare complexity
        output += f"**COMPLEXITY ANALYSIS:**\n"
        output += f"- {policy1_title}: {analysis1['complexity_score']} complexity score\n"
        output += f"- {policy2_title}: {analysis2['complexity_score']} complexity score\n\n"
        
        # Recommendations
        if analysis1['complexity_score'] > analysis2['complexity_score']:
            output += f"📝 **RECOMMENDATION:** {policy1_title} appears more complex and may require additional compliance resources.\n"
        elif analysis2['complexity_score'] > analysis1['complexity_score']:
            output += f"📝 **RECOMMENDATION:** {policy2_title} appears more complex and may require additional compliance resources.\n"
        
        return output
    
    def _analyze_for_comparison(self, text: str) -> Dict[str, Any]:
        """Analyze text for comparison purposes"""
        sentences = self._split_into_sentences(text)
        
        mandatory_keywords = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(keyword in sentence_lower for keyword in self.compliance_keywords["mandatory"]):
                # Extract key terms from mandatory sentences
                words = re.findall(r'\b\w+\b', sentence_lower)
                mandatory_keywords.extend([w for w in words if len(w) > 4])
        
        complexity_score = len(sentences) + len(set(mandatory_keywords)) * 2
        
        return {
            "mandatory_keywords": list(set(mandatory_keywords)),
            "complexity_score": complexity_score,
            "sentence_count": len(sentences)
        }
    
    def extract_stakeholders(self, document_text: str) -> str:
        """
        Extract stakeholders and their responsibilities from a policy document
        """
        logger.info("Extracting stakeholders from policy document")
        
        # Common stakeholder patterns
        stakeholder_patterns = [
            r"(financial institutions?|banks?|credit unions?)",
            r"(agencies?|departments?|bureaus?)",
            r"(consumers?|individuals?|citizens?)",
            r"(businesses?|companies?|corporations?|entities?)",
            r"(providers?|services?|platforms?)",
            r"(regulators?|supervisors?|authorities?)"
        ]
        
        stakeholders = {}
        sentences = self._split_into_sentences(document_text)
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            for pattern in stakeholder_patterns:
                matches = re.findall(pattern, sentence_lower)
                for match in matches:
                    stakeholder = match.strip()
                    if stakeholder not in stakeholders:
                        stakeholders[stakeholder] = []
                    stakeholders[stakeholder].append(sentence.strip())
        
        # Format output
        output = "**Stakeholder Responsibility Analysis**\n\n"
        
        for stakeholder, responsibilities in stakeholders.items():
            if responsibilities:
                output += f"**{stakeholder.upper()}:**\n"
                for i, resp in enumerate(responsibilities[:3], 1):  # Limit to 3 per stakeholder
                    output += f"{i}. {resp[:200]}{'...' if len(resp) > 200 else ''}\n"
                output += "\n"
        
        return output

class CustomPolicyTool:
    """aiXplain-compatible wrapper for policy analysis"""
    
    def __init__(self):
        self.analyzer = PolicyAnalysisTool()
    
    def analyze_policy_compliance(self, document_text: str, document_title: str = "") -> str:
        """
        Analyze compliance requirements in a policy document
        
        Args:
            document_text: Full text of the policy document
            document_title: Optional title of the document
        """
        return self.analyzer.analyze_compliance_requirements(document_text, document_title)
    
    def extract_policy_stakeholders(self, document_text: str) -> str:
        """
        Extract stakeholders and their responsibilities
        
        Args:
            document_text: Full text of the policy document
        """
        return self.analyzer.extract_stakeholders(document_text)

if __name__ == "__main__":
    # Test the custom analysis tool
    tool = CustomPolicyTool()
    
    # Sample policy text for testing
    sample_text = """
    Financial institutions must implement anti-money laundering procedures within 180 days. 
    Entities shall not engage in transactions with sanctioned individuals. 
    Companies may voluntarily adopt enhanced due diligence measures.
    Violations may result in penalties up to $500,000 per incident.
    This regulation becomes effective on January 1, 2024.
    """
    
    print("Testing compliance analysis:")
    result = tool.analyze_policy_compliance(sample_text, "Sample AML Regulation")
    print(result)
    
    print("\n" + "="*50 + "\n")
    
    print("Testing stakeholder extraction:")
    stakeholders = tool.extract_policy_stakeholders(sample_text)
    print(stakeholders)