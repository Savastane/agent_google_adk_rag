import os
from io import BytesIO
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Path, status
from google.adk.runtime.agents import run_agent

from .agent import rag_agent
from .tools import document_processor

app = FastAPI(
    title="RAG Agent",
    description="An agent that uses a vector and graph database for RAG.",
)

@app.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Endpoint to check if the API is running.
    """
    return {"status": "RAG Agent is running"}


@app.post("/documents/", status_code=status.HTTP_201_CREATED)
async def upload_document(subject: str = Form(...), file: UploadFile = File(...)):
    """
    Uploads a document, extracts its content, and ingests it into the databases.
    Supported formats: .pdf, .docx, .txt, .md
    """
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in document_processor.EXTRACTORS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_extension}' not supported. Supported types are {list(document_processor.EXTRACTORS.keys())}"
        )

    try:
        file_stream = BytesIO(await file.read())
        extractor = document_processor.EXTRACTORS[file_extension]
        content = extractor(file_stream)
        doc_id = os.path.splitext(file.filename)[0]
        
        result = document_processor.add_document(doc_id, content, subject)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process file: {e}")

@app.delete("/documents/{doc_id}", status_code=status.HTTP_200_OK)
async def delete_document(doc_id: str = Path(..., description="The ID of the document to delete")):
    """
    Deletes a document from the databases.
    """
    try:
        result = document_processor.remove_document(doc_id)
        if result["status"] == "not_found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["message"])
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete document: {e}")

# The ADK runtime will automatically discover this endpoint and
# generate an OpenAPI spec for it.
run_agent(rag_agent, app)
