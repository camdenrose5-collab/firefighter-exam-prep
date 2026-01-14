"""
RAG Engine
Handles retrieval from ChromaDB and context assembly.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional

import chromadb
from chromadb.config import Settings


class RAGEngine:
    """
    Retrieval-Augmented Generation engine.
    Queries ChromaDB for relevant chunks and assembles context.
    """
    
    def __init__(self, chroma_dir: str):
        self.chroma_dir = Path(chroma_dir)
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.chroma_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        
        # Get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="firefighter_docs",
            metadata={"hnsw:space": "cosine"},
        )
    
    def retrieve(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: The search query
            document_ids: Optional list of document IDs to filter by
            top_k: Number of results to return
            
        Returns:
            List of retrieved chunks with metadata
        """
        # Build where filter for document IDs
        where_filter = None
        if document_ids:
            where_filter = {"document_id": {"$in": document_ids}}
        
        # Query the collection
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter,
            include=["documents", "metadatas", "distances"],
        )
        
        # Format results
        retrieved_chunks = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else None
                
                retrieved_chunks.append({
                    "text": doc,
                    "source": metadata.get("filename", "Unknown"),
                    "document_id": metadata.get("document_id"),
                    "chunk_index": metadata.get("chunk_index"),
                    "relevance_score": 1 - distance if distance else None,  # Convert distance to similarity
                })
        
        return retrieved_chunks
    
    def build_context(
        self,
        query: str,
        document_ids: Optional[List[str]] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Build context for LLM from retrieved chunks.
        
        Returns:
            Dict with 'context' string and 'citations' list
        """
        chunks = self.retrieve(query, document_ids, top_k)
        
        if not chunks:
            return {
                "context": "",
                "citations": [],
            }
        
        # Build context string
        context_parts = []
        citations = []
        
        for i, chunk in enumerate(chunks):
            citation_num = i + 1
            context_parts.append(f"[{citation_num}] {chunk['text']}")
            citations.append({
                "id": citation_num,
                "source": chunk["source"],
                "excerpt": chunk["text"][:200] + "..." if len(chunk["text"]) > 200 else chunk["text"],
            })
        
        return {
            "context": "\n\n".join(context_parts),
            "citations": citations,
        }
