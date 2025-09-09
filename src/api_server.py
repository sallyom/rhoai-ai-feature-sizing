"""
FastAPI Server for File Upload and RAG Management
Provides REST endpoints for dynamic content upload
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn

from src.upload_service import upload_service


# Create FastAPI app
app = FastAPI(
    title="RHOAI AI Feature Sizing - Upload API",
    description="API for uploading files and managing RAG content",
    version="1.0.0"
)

# Add CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "upload-api"}


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file and add it to RAG indices
    
    Args:
        file: Uploaded file
        
    Returns:
        JSON response with upload and indexing results
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Read file content
        content = await file.read()
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="Empty file")
        
        # Process upload
        result = await upload_service.upload_file(file.filename, content)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@app.get("/api/uploads")
async def list_uploads():
    """
    List all uploaded files
    
    Returns:
        JSON list of uploaded files with metadata
    """
    try:
        files = await upload_service.list_uploaded_files()
        return JSONResponse(content={"files": files})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")


@app.delete("/api/uploads/{filename}")
async def delete_upload(filename: str):
    """
    Delete an uploaded file
    
    Args:
        filename: Name of file to delete
        
    Returns:
        JSON response with deletion result
    """
    try:
        result = await upload_service.delete_uploaded_file(filename)
        
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@app.get("/api/rag/status")
async def rag_status():
    """
    Get RAG system status and agent information
    
    Returns:
        JSON with RAG system information
    """
    try:
        # Get agent directories
        from pathlib import Path
        output_dir = Path("/app/output/python-rag")
        
        agents = []
        if output_dir.exists():
            for agent_dir in output_dir.glob("*"):
                if agent_dir.is_dir():
                    # Check if index exists
                    has_index = (agent_dir / "docstore.json").exists()
                    agents.append({
                        "name": agent_dir.name,
                        "has_index": has_index,
                        "index_path": str(agent_dir)
                    })
        
        return JSONResponse(content={
            "status": "active",
            "total_agents": len(agents),
            "agents": agents
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get RAG status: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)