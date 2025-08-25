"""
Vector Store Module for Policy Navigator Agent
Handles creation and management of vector indices using ChromaDB
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import json
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorStoreManager:
    """Manages vector storage and retrieval using ChromaDB"""
    
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        # Initialize sentence transformer model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Collection name
        self.collection_name = "policy_documents"
        
        # Create or get collection
        try:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Policy and regulation documents"}
            )
        except Exception:
            # Collection already exists
            self.collection = self.client.get_collection(name=self.collection_name)
        
        logger.info(f"Vector store initialized with collection: {self.collection_name}")
    
    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a list of texts"""
        logger.info(f"Creating embeddings for {len(texts)} texts...")
        embeddings = self.embedding_model.encode(texts).tolist()
        return embeddings
    
    def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the vector store"""
        logger.info(f"Adding {len(documents)} documents to vector store...")
        
        # Prepare data for ChromaDB
        ids = []
        documents_texts = []
        metadatas = []
        
        for doc in documents:
            ids.append(doc["id"])
            # Combine title and content for better search
            full_text = f"{doc['title']} {doc['content']}"
            documents_texts.append(full_text)
            
            # Prepare metadata (ensure all values are strings)
            metadata = doc.get("metadata", {})
            clean_metadata = {}
            for key, value in metadata.items():
                if isinstance(value, list):
                    clean_metadata[key] = ", ".join(str(v) for v in value)
                else:
                    clean_metadata[key] = str(value)
            
            # Add document-level metadata
            clean_metadata.update({
                "title": doc["title"],
                "doc_id": doc["id"]
            })
            metadatas.append(clean_metadata)
        
        # Create embeddings
        embeddings = self.create_embeddings(documents_texts)
        
        try:
            # Add to collection
            self.collection.add(
                embeddings=embeddings,
                documents=documents_texts,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Successfully added {len(documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error adding documents to vector store: {e}")
            # If documents already exist, we can update them
            try:
                self.collection.upsert(
                    embeddings=embeddings,
                    documents=documents_texts,
                    metadatas=metadatas,
                    ids=ids
                )
                logger.info(f"Successfully updated {len(documents)} documents in vector store")
            except Exception as e2:
                logger.error(f"Error updating documents in vector store: {e2}")
                raise
    
    def search_documents(self, query: str, n_results: int = 5) -> Dict[str, Any]:
        """Search for relevant documents based on a query"""
        logger.info(f"Searching for documents with query: '{query}'")
        
        try:
            # Create embedding for the query
            query_embedding = self.embedding_model.encode([query]).tolist()[0]
            
            # Search in the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = {
                "query": query,
                "results": []
            }
            
            if results["ids"] and len(results["ids"][0]) > 0:
                for i in range(len(results["ids"][0])):
                    formatted_results["results"].append({
                        "id": results["ids"][0][i],
                        "document": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i],
                        "relevance_score": 1 - results["distances"][0][i]  # Convert distance to relevance
                    })
            
            logger.info(f"Found {len(formatted_results['results'])} relevant documents")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return {"query": query, "results": [], "error": str(e)}
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store collection"""
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "embedding_model": "all-MiniLM-L6-v2",
                "persist_directory": str(self.persist_directory)
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
    
    def delete_collection(self) -> bool:
        """Delete the entire collection (use with caution)"""
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info(f"Deleted collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection: {e}")
            return False

class VectorSearchTool:
    """Tool for searching policy documents - can be used as an aiXplain tool"""
    
    def __init__(self, vector_store: VectorStoreManager):
        self.vector_store = vector_store
    
    def search_policy_documents(self, query: str, num_results: int = 3) -> str:
        """
        Search for policy documents relevant to a query
        Returns formatted text with search results
        """
        results = self.vector_store.search_documents(query, num_results)
        
        if not results["results"]:
            return f"No relevant policy documents found for query: '{query}'"
        
        formatted_output = f"Found {len(results['results'])} relevant policy documents for '{query}':\n\n"
        
        for i, result in enumerate(results["results"], 1):
            metadata = result["metadata"]
            formatted_output += f"{i}. **{metadata.get('title', 'Unknown Title')}**\n"
            formatted_output += f"   Document ID: {result['id']}\n"
            formatted_output += f"   Relevance Score: {result['relevance_score']:.3f}\n"
            formatted_output += f"   Source: {metadata.get('source', 'Unknown')}\n"
            
            if 'type' in metadata:
                formatted_output += f"   Type: {metadata['type']}\n"
            if 'agency' in metadata:
                formatted_output += f"   Agency: {metadata['agency']}\n"
            if 'date' in metadata:
                formatted_output += f"   Date: {metadata['date']}\n"
            
            # Add snippet of the document
            doc_text = result["document"]
            snippet = doc_text[:300] + "..." if len(doc_text) > 300 else doc_text
            formatted_output += f"   Content: {snippet}\n\n"
        
        return formatted_output

if __name__ == "__main__":
    # Test vector store
    from data_ingestion import DataIngestionManager
    
    # Create some test data
    ingestion_manager = DataIngestionManager()
    documents = ingestion_manager.ingest_all_data()
    
    # Create vector store and add documents
    vector_store = VectorStoreManager()
    vector_store.add_documents(documents)
    
    # Test search
    search_tool = VectorSearchTool(vector_store)
    results = search_tool.search_policy_documents("digital assets cryptocurrency")
    print(results)
    
    # Print collection stats
    stats = vector_store.get_collection_stats()
    print(f"\nCollection Stats: {stats}")