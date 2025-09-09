"""
File Upload Service for Dynamic RAG Content
Handles file uploads and real-time RAG indexing
"""

import os
import asyncio
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from llama_index.core import Document, VectorStoreIndex
from llama_index.core.storage import StorageContext
from llama_index.core.indices import load_index_from_storage
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import SimpleDirectoryReader

from src.settings import init_settings


class UploadService:
    """Service for handling file uploads and dynamic RAG indexing"""
    
    def __init__(self, upload_dir: str = "/app/uploads", output_dir: str = "/app/output"):
        self.upload_dir = Path(upload_dir)
        self.output_dir = Path(output_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Initialize LlamaIndex settings
        init_settings()
        
        # Text splitter for chunking
        self.text_splitter = SentenceSplitter(
            chunk_size=512,
            chunk_overlap=50
        )
    
    async def upload_file(self, filename: str, content: bytes) -> dict:
        """
        Upload a file and add it to RAG indices
        
        Args:
            filename: Name of the uploaded file
            content: File content as bytes
            
        Returns:
            dict: Upload result with file info and indexing status
        """
        try:
            # Save uploaded file
            file_path = self.upload_dir / filename
            
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # Process file for RAG
            index_result = await self._index_uploaded_file(file_path)
            
            return {
                "status": "success",
                "filename": filename,
                "file_path": str(file_path),
                "file_size": len(content),
                "upload_time": datetime.now().isoformat(),
                "indexing_result": index_result
            }
            
        except Exception as e:
            return {
                "status": "error",
                "filename": filename,
                "error": str(e)
            }
    
    async def _index_uploaded_file(self, file_path: Path) -> dict:
        """
        Index an uploaded file into all agent RAG stores
        
        Args:
            file_path: Path to the uploaded file
            
        Returns:
            dict: Indexing results per agent
        """
        try:
            # Load the document
            reader = SimpleDirectoryReader(input_files=[str(file_path)])
            documents = reader.load_data()
            
            if not documents:
                return {"status": "error", "message": "No content extracted from file"}
            
            # Add metadata
            for doc in documents:
                doc.metadata.update({
                    "source_type": "uploaded",
                    "upload_time": datetime.now().isoformat(),
                    "filename": file_path.name,
                    "file_path": str(file_path)
                })
            
            # Get list of existing agent indices
            agent_dirs = [d for d in self.output_dir.glob("python-rag/*") if d.is_dir()]
            
            results = {}
            
            # Add to each agent's index
            for agent_dir in agent_dirs:
                agent_name = agent_dir.name
                try:
                    # Load existing index
                    storage_context = StorageContext.from_defaults(persist_dir=str(agent_dir))
                    index = load_index_from_storage(storage_context)
                    
                    # Add new documents to index
                    for doc in documents:
                        index.insert(doc)
                    
                    # Persist updated index
                    index.storage_context.persist(persist_dir=str(agent_dir))
                    
                    results[agent_name] = {
                        "status": "success",
                        "documents_added": len(documents)
                    }
                    
                except Exception as e:
                    results[agent_name] = {
                        "status": "error", 
                        "error": str(e)
                    }
            
            return {
                "status": "success",
                "total_documents": len(documents),
                "agents_updated": len([r for r in results.values() if r["status"] == "success"]),
                "agent_results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def list_uploaded_files(self) -> List[dict]:
        """
        List all uploaded files with metadata
        
        Returns:
            List of file information dictionaries
        """
        files = []
        
        for file_path in self.upload_dir.glob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                files.append({
                    "filename": file_path.name,
                    "file_path": str(file_path),
                    "size": stat.st_size,
                    "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
        
        return sorted(files, key=lambda x: x["modified_time"], reverse=True)
    
    async def delete_uploaded_file(self, filename: str) -> dict:
        """
        Delete an uploaded file (note: doesn't remove from indices)
        
        Args:
            filename: Name of file to delete
            
        Returns:
            dict: Deletion result
        """
        try:
            file_path = self.upload_dir / filename
            
            if not file_path.exists():
                return {"status": "error", "message": "File not found"}
            
            file_path.unlink()
            
            return {
                "status": "success",
                "message": f"File {filename} deleted"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Global service instance
upload_service = UploadService()