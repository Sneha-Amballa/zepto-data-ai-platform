"""
FastAPI Server Module

Defines the web API wrapper around the LangGraph support assistant pipeline.
Supports POST /ask endpoint for policy and general customer service questions.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Import LangGraph graph, Pydantic response schema, and ingestion function
from graph import graph
from schema import AnswerResponse
from ingest import ingest_policies


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan manager to verify ChromaDB persistence directory and collection
    presence upon startup. Runs ingestion automatically if not found.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, "chroma_db")

    # Check if persistent database exists and has collection files
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
    """
    API payload for query requests.
    """
    query: str = Field(
        ...,
        examples=["What is your delivery fee?"],
        description="The customer's question."
    )


@app.post("/ask", response_model=AnswerResponse)
async def ask_question(request: QueryRequest) -> AnswerResponse:
    """
    Takes a query string, runs it through the LangGraph intent classification
    and retrieval pipeline, and returns a validated AnswerResponse containing the answer,
    sources, and confidence metrics.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        # Execute the StateGraph pipeline
        result = graph.invoke({"query": request.query})

        # Format and validate final result against the AnswerResponse schema
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
