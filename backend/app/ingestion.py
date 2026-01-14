"""
PDF Ingestion Pipeline
Handles PDF upload, text extraction with MarkItDown, 
chunking, and embedding into ChromaDB.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any

from fastapi import UploadFile
import chromadb
from chromadb.config import Settings

# Try to import markitdown, fall back to basic extraction if not available
try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    print("⚠️ MarkItDown not available, using fallback PDF extraction")


class PDFIngestionPipeline:
    """
    Pipeline for ingesting PDF documents into the vector store.
    """
    
    def __init__(self, upload_dir: str, chroma_dir: str):
        self.upload_dir = Path(upload_dir)
        self.chroma_dir = Path(chroma_dir)
        self.metadata_file = self.upload_dir / "metadata.json"
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=str(self.chroma_dir),
            settings=Settings(anonymized_telemetry=False),
        )
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="firefighter_docs",
            metadata={"hnsw:space": "cosine"},
        )
        
        # Load existing metadata
        self.documents_metadata = self._load_metadata()
        
        # Initialize MarkItDown if available
        if MARKITDOWN_AVAILABLE:
            self.md_converter = MarkItDown()
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load document metadata from disk."""
        if self.metadata_file.exists():
            with open(self.metadata_file, "r") as f:
                return json.load(f)
        return {}
    
    def _save_metadata(self):
        """Save document metadata to disk."""
        with open(self.metadata_file, "w") as f:
            json.dump(self.documents_metadata, f, indent=2)
    
    async def process_pdf(self, file: UploadFile, document_id: str) -> Dict[str, Any]:
        """
        Process a PDF file:
        1. Save to disk
        2. Extract text with MarkItDown
        3. Chunk the text
        4. Index into ChromaDB
        """
        # Save file to disk
        file_path = self.upload_dir / f"{document_id}.pdf"
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Extract text
        text = self._extract_text(str(file_path))
        
        # Chunk the text
        chunks = self._chunk_text(text, chunk_size=1000, overlap=200)
        
        # Create embeddings and store in ChromaDB
        # Note: ChromaDB will use its default embedding function
        chunk_ids = []
        chunk_texts = []
        chunk_metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{document_id}_chunk_{i}"
            chunk_ids.append(chunk_id)
            chunk_texts.append(chunk["text"])
            chunk_metadatas.append({
                "document_id": document_id,
                "filename": file.filename,
                "chunk_index": i,
                "start_char": chunk["start"],
                "end_char": chunk["end"],
            })
        
        # Add to collection
        if chunk_texts:
            self.collection.add(
                ids=chunk_ids,
                documents=chunk_texts,
                metadatas=chunk_metadatas,
            )
        
        # Save metadata
        self.documents_metadata[document_id] = {
            "filename": file.filename,
            "chunks_count": len(chunks),
            "file_path": str(file_path),
        }
        self._save_metadata()
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "chunks_count": len(chunks),
        }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from PDF using MarkItDown or fallback."""
        if MARKITDOWN_AVAILABLE:
            try:
                result = self.md_converter.convert(file_path)
                return result.text_content
            except Exception as e:
                print(f"⚠️ MarkItDown extraction failed: {e}")
        
        # Fallback: Try PyPDF2 or return placeholder
        try:
            import pypdf
            reader = pypdf.PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            return f"[PDF content from {file_path} - install pypdf for text extraction]"
    
    def _chunk_text(
        self, 
        text: str, 
        chunk_size: int = 1000, 
        overlap: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        Uses sentence boundaries when possible.
        """
        if not text:
            return []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to find a sentence boundary
            if end < len(text):
                # Look for sentence endings
                for boundary in [". ", ".\n", "! ", "? "]:
                    last_boundary = text[start:end].rfind(boundary)
                    if last_boundary != -1:
                        end = start + last_boundary + len(boundary)
                        break
            
            chunk_text = text[start:end].strip()
            if chunk_text:
                chunks.append({
                    "text": chunk_text,
                    "start": start,
                    "end": end,
                })
            
            # Move start with overlap
            start = end - overlap if end < len(text) else len(text)
        
        return chunks
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all indexed documents."""
        return [
            {
                "document_id": doc_id,
                "filename": info["filename"],
                "chunks_count": info["chunks_count"],
            }
            for doc_id, info in self.documents_metadata.items()
        ]
