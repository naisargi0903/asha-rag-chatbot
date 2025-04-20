"""Vector store for semantic search."""

import logging
from typing import Dict, Any, List, Optional
import numpy as np
from pathlib import Path
import os
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class VectorStore:
    """Manages vector storage and retrieval."""
    
    def __init__(self, path: Optional[str] = None):
        """Initialize the vector store.
        
        Args:
            path: Path to store vectors
        """
        self.path = path or os.environ.get('VECTOR_DB_PATH', 'data/vector_db')
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray = np.array([])
        self._load_store()
    
    def _load_store(self):
        """Load the vector store from disk."""
        try:
            store_path = Path(self.path)
            if store_path.exists():
                with open(store_path, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get('documents', [])
                    self.embeddings = np.array(data.get('embeddings', []))
                logger.info(f"Loaded {len(self.documents)} documents from vector store")
        except Exception as e:
            logger.error(f"Error loading vector store: {str(e)}")
            # Initialize empty store
            self.documents = []
            self.embeddings = np.array([])
    
    def _save_store(self):
        """Save the vector store to disk."""
        try:
            store_path = Path(self.path)
            store_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                'documents': self.documents,
                'embeddings': self.embeddings.tolist(),
                'last_updated': datetime.now().isoformat()
            }
            
            with open(store_path, 'w') as f:
                json.dump(data, f)
                
            logger.info(f"Saved {len(self.documents)} documents to vector store")
        except Exception as e:
            logger.error(f"Error saving vector store: {str(e)}")
    
    def add(self, text: str, metadata: Dict[str, Any]):
        """Add a document to the store.
        
        Args:
            text: Document text
            metadata: Document metadata
        """
        try:
            document = {
                'text': text,
                'metadata': metadata,
                'timestamp': datetime.now().isoformat()
            }
            
            self.documents.append(document)
            self._save_store()
            
        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: np.ndarray):
        """Add multiple documents with their embeddings.
        
        Args:
            documents: List of documents
            embeddings: Document embeddings
        """
        try:
            if len(documents) != len(embeddings):
                raise ValueError("Number of documents and embeddings must match")
            
            for doc, emb in zip(documents, embeddings):
                self.documents.append(doc)
                if len(self.embeddings) == 0:
                    self.embeddings = np.array([emb])
                else:
                    self.embeddings = np.vstack([self.embeddings, emb])
            
            self._save_store()
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
    
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents.
        
        Args:
            query_embedding: Query embedding
            k: Number of results to return
            
        Returns:
            List of similar documents
        """
        try:
            if len(self.embeddings) == 0:
                return []
            
            # Calculate cosine similarity
            similarities = np.dot(self.embeddings, query_embedding) / (
                np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Get top k results
            top_k_indices = np.argsort(similarities)[-k:][::-1]
            
            results = []
            for idx in top_k_indices:
                results.append({
                    'text': self.documents[idx]['text'],
                    'metadata': self.documents[idx]['metadata'],
                    'similarity': float(similarities[idx])
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            return []
    
    def get_size(self) -> int:
        """Get the number of documents in the store.
        
        Returns:
            Number of documents
        """
        return len(self.documents)
    
    def clear(self):
        """Clear the vector store."""
        try:
            self.documents = []
            self.embeddings = np.array([])
            self._save_store()
            logger.info("Vector store cleared")
        except Exception as e:
            logger.error(f"Error clearing vector store: {str(e)}")