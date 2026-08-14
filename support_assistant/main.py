"""
FastAPI Server for the customer support assistant pipeline.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Imports
from graph import graph
from schema import AnswerResponse
from ingest import ingest_policies


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan to verify and auto-ingest ChromaDB database on startup."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, "chroma_db")

    # Check if persistent database exists
    db_exists = os.path.exists(db_dir) and any(
        os.path.isdir(os.path.join(db_dir, item)) for item in os.listdir(db_dir)
    ) if os.path.exists(db_dir) else False

    if not db_exists:
        print("[Startup] ChromaDB persistent database files not found. Triggering auto-ingestion...")
        ingest_policies()
    else:
        print("[Startup] Reusing existing persistent ChromaDB database collection 'zepto_policies'.")
    yield


app = FastAPI(
    title="Zepto Customer Support Assistant",
    description="FastAPI interface for retrieving Zepto customer service policies.",
    version="1.0.0",
    lifespan=lifespan
)


class QueryRequest(BaseModel):
    """API payload for customer query."""
    query: str = Field(
        ...,
        examples=["What is your delivery fee?"],
        description="The customer's question."
    )


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QueryRequest) -> AnswerResponse:
    """Routes query request through StateGraph and returns validated response."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Execute pipeline
        result = graph.invoke({"query": request.query})

        # Validate response
        response = AnswerResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"]
        )
        return response

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing support assistant pipeline: {str(e)}"
        )
