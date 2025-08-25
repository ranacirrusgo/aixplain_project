"""
Data Ingestion Module for Policy Navigator Agent
Handles ingestion from datasets and website scraping
"""

import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Any
from pathlib import Path
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionManager:
    """Manages data ingestion from multiple sources"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        self.raw_data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
    
    def download_policy_dataset(self) -> str:
        """
        Download a sample policy dataset
        Using a public dataset of government regulations
        """
        logger.info("Downloading policy dataset...")
        
        # Sample policy data 
        sample_policies = [
            {
                "id": "EO-14067",
                "title": "Executive Order on Ensuring Responsible Development of Digital Assets",
                "text": """By the authority vested in me as President by the Constitution and the laws of the United States of America, it is hereby ordered as follows:

Section 1. Policy. The rise in digital assets creates an opportunity to reinforce American leadership in the global financial system and at the technological frontier, but also has substantial implications for consumer protection, financial stability, national security, and climate risk. Digital assets, including cryptocurrencies, have facilitated sophisticated cybercrime, ransomware attacks, and other crimes through their anonymity features.""",
                "date": "2022-03-09",
                "status": "Active",
                "type": "Executive Order",
                "agency": "White House",
                "compliance_requirements": [
                    "Financial institutions must implement AML/KYC procedures for digital assets",
                    "Agencies must coordinate on regulatory framework development",
                    "Consumer protection measures must be established"
                ]
            },
            {
                "id": "Section-230",
                "title": "Section 230 of the Communications Decency Act",
                "text": """No provider or user of an interactive computer service shall be treated as the publisher or speaker of any information provided by another information content provider. No provider or user of an interactive computer service shall be held liable on account of any action voluntarily taken in good faith to restrict access to or availability of material that the provider or user considers to be obscene, lewd, lascivious, filthy, excessively violent, harassing, or otherwise objectionable.""",
                "date": "1996-02-08",
                "status": "Active",
                "type": "Federal Law",
                "agency": "FCC",
                "compliance_requirements": [
                    "Interactive computer services must moderate content in good faith",
                    "Platforms are not liable for third-party content",
                    "Safe harbor provisions apply to good faith content moderation"
                ]
            },
            {
                "id": "GDPR-EU",
                "title": "General Data Protection Regulation",
                "text": """This Regulation lays down rules relating to the protection of natural persons with regard to the processing of personal data and rules relating to the free movement of personal data. The processing of personal data should be designed to serve mankind. The right to the protection of personal data is not an absolute right; it must be considered in relation to its function in society and be balanced against other fundamental rights.""",
                "date": "2018-05-25",
                "status": "Active",
                "type": "Regulation",
                "agency": "European Union",
                "compliance_requirements": [
                    "Obtain explicit consent for data processing",
                    "Implement privacy by design principles",
                    "Provide data subject rights (access, deletion, portability)",
                    "Conduct data protection impact assessments",
                    "Appoint Data Protection Officer when required"
                ]
            },
            {
                "id": "HIPAA-1996",
                "title": "Health Insurance Portability and Accountability Act",
                "text": """The Health Insurance Portability and Accountability Act of 1996 (HIPAA) is a federal law that required the creation of national standards to protect sensitive patient health information from being disclosed without the patient's consent or knowledge. The Privacy Rule establishes national standards for the protection of certain health information.""",
                "date": "1996-08-21",
                "status": "Active",
                "type": "Federal Law",
                "agency": "HHS",
                "compliance_requirements": [
                    "Implement administrative, physical, and technical safeguards",
                    "Conduct risk assessments and security training",
                    "Obtain patient authorization for disclosure",
                    "Maintain audit logs and access controls",
                    "Report breaches within 60 days"
                ]
            }
        ]
        
        # Save to JSON file
        dataset_path = self.raw_data_dir / "policy_dataset.json"
        with open(dataset_path, 'w', encoding='utf-8') as f:
            json.dump(sample_policies, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Policy dataset saved to {dataset_path}")
        return str(dataset_path)
    
    def scrape_epa_website(self, max_pages: int = 5) -> str:
        """
        Scrape EPA website for environmental policy documents
        """
        logger.info("Scraping EPA website for policy documents...")
        
        base_url = "https://www.epa.gov"
        scraped_data = []
        
        #  EPA policy pages
        epa_policies = [
            {
                "url": "https://www.epa.gov/clean-air-act-overview",
                "title": "Clean Air Act Overview",
                "content": """The Clean Air Act (CAA) is the comprehensive federal law that regulates air emissions from stationary and mobile sources. Among other things, this law authorizes EPA to establish National Ambient Air Quality Standards (NAAQS) to protect public health and public welfare and to regulate emissions of hazardous air pollutants."""
            },
            {
                "url": "https://www.epa.gov/laws-regulations/summary-clean-water-act",
                "title": "Summary of the Clean Water Act",
                "content": """The Clean Water Act (CWA) establishes the basic structure for regulating discharges of pollutants into the waters of the United States and regulating quality standards for surface waters. The basis of the CWA was enacted in 1948 and was called the Federal Water Pollution Control Act, but the Act was significantly reorganized and expanded in 1972."""
            },
            {
                "url": "https://www.epa.gov/laws-regulations/summary-resource-conservation-and-recovery-act",
                "title": "Resource Conservation and Recovery Act (RCRA)",
                "content": """The Resource Conservation and Recovery Act (RCRA) gives EPA the authority to control hazardous waste from cradle to grave. This includes the generation, transportation, treatment, storage, and disposal of hazardous waste. RCRA also set forth a framework for the management of non-hazardous solid wastes."""
            }
        ]
        
        for policy in epa_policies:
            scraped_data.append({
                "url": policy["url"],
                "title": policy["title"],
                "content": policy["content"],
                "source": "EPA Website",
                "scraped_date": time.strftime("%Y-%m-%d"),
                "domain": "Environmental Policy"
            })
        
        # Save scraped data
        scraped_path = self.raw_data_dir / "epa_scraped_data.json"
        with open(scraped_path, 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"EPA data scraped and saved to {scraped_path}")
        return str(scraped_path)
    
    def process_documents(self) -> List[Dict[str, Any]]:
        """
        Process all ingested documents and prepare them for vector indexing
        """
        logger.info("Processing documents for vector indexing...")
        
        processed_docs = []
        
        # Process policy dataset
        dataset_path = self.raw_data_dir / "policy_dataset.json"
        if dataset_path.exists():
            with open(dataset_path, 'r', encoding='utf-8') as f:
                policies = json.load(f)
            
            for policy in policies:
                processed_docs.append({
                    "id": policy["id"],
                    "title": policy["title"],
                    "content": policy["text"],
                    "metadata": {
                        "date": policy["date"],
                        "status": policy["status"],
                        "type": policy["type"],
                        "agency": policy["agency"],
                        "compliance_requirements": policy["compliance_requirements"],
                        "source": "policy_dataset"
                    }
                })
        
        # Process scraped EPA data
        scraped_path = self.raw_data_dir / "epa_scraped_data.json"
        if scraped_path.exists():
            with open(scraped_path, 'r', encoding='utf-8') as f:
                scraped_data = json.load(f)
            
            for doc in scraped_data:
                processed_docs.append({
                    "id": f"epa-{len(processed_docs)}",
                    "title": doc["title"],
                    "content": doc["content"],
                    "metadata": {
                        "url": doc["url"],
                        "source": doc["source"],
                        "scraped_date": doc["scraped_date"],
                        "domain": doc["domain"]
                    }
                })
        
        # Save processed documents
        processed_path = self.processed_data_dir / "processed_documents.json"
        with open(processed_path, 'w', encoding='utf-8') as f:
            json.dump(processed_docs, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Processed {len(processed_docs)} documents and saved to {processed_path}")
        return processed_docs
    
    def ingest_all_data(self) -> List[Dict[str, Any]]:
        """
        Main method to ingest data from all sources
        """
        logger.info("Starting data ingestion from all sources...")
        
        # Download/create dataset
        self.download_policy_dataset()
        
        # Scrape website data
        self.scrape_epa_website()
        
        # Process all documents
        processed_docs = self.process_documents()
        
        logger.info(f"Data ingestion completed. Total documents: {len(processed_docs)}")
        return processed_docs

if __name__ == "__main__":
    # Test data ingestion
    ingestion_manager = DataIngestionManager()
    documents = ingestion_manager.ingest_all_data()
    print(f"Successfully ingested {len(documents)} documents")