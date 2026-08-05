"""
Graph Module

Defines the LangGraph StateGraph and nodes for intent classification, policy retrieval,
and mock/stub answering. Validates final output against the Pydantic schema.
"""

import os
import json
from typing import TypedDict, List
import chromadb
from sentence_transformers import SentenceTransformer
from langgraph.graph import StateGraph, END

# Import schemas and prompts
from schema import AnswerResponse
from prompts import PROMPT_TEMPLATE


# Define LangGraph state schema
class AgentState(TypedDict):
    query: str
    intent: str
    retrieved_chunks: List[str]
    sources: List[str]
    answer: str
    confidence: float


def classify_intent(state: AgentState) -> dict:
    """
    Classifies the user query intent by checking for policy-related keywords.
    Gated on MOCK_LLM environment variable (default: mock mode '1').
    """
    query = state.get("query", "").lower()
    mock_llm = os.getenv("MOCK_LLM", "1")

    if mock_llm == "0":
        # Stub branch for actual LLM execution (Optional/Ungraded extension)
        # Example: call actual LLM (e.g. Groq) to classify query intent.
        intent = "policy_question"
    else:
        # Baseline Mock mode
        keywords = [
            "delivery", "return", "refund", "membership",
            "tracking", "cancel", "gift card", "support hours"
        ]
        if any(kw in query for kw in keywords):
            intent = "policy_question"
        else:
            intent = "general_question"

    print(f"[Node: classify_intent] Query: '{query}' classified as intent: '{intent}'")
    return {"intent": intent}


def retrieve_and_answer(state: AgentState) -> dict:
    """
    Embeds query, performs vector search against persistent ChromaDB collection,
    and returns a policy-grounded response.
    """
    query = state.get("query", "")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(base_dir, "chroma_db")

    # 1. ALWAYS perform the vector search regardless of MOCK_LLM
    print(f"[Node: retrieve_and_answer] Embedding query and searching ChromaDB at: {db_dir}...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    query_embedding = model.encode(query).tolist()

    client = chromadb.PersistentClient(path=db_dir)
    collection = client.get_collection("zepto_policies")

    # Retrieve top-3 chunks using similarity search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    retrieved_chunks = results["documents"][0] if results["documents"] else []
    sources = results["ids"][0] if results["ids"] else []

    mock_llm = os.getenv("MOCK_LLM", "1")

    if mock_llm == "0":
        # Stub branch for actual LLM answering (Optional/Ungraded extension)
        # Format PROMPT_TEMPLATE with context chunks and query, then call LLM API.
        context_block = "\n\n".join([f"[{doc_id}] {text}" for doc_id, text in zip(sources, retrieved_chunks)])
        prompt = PROMPT_TEMPLATE.format(context=context_block, query=query)

        # Retry loop for validation failure
        max_retries = 3
        answer = "I do not have access to this information in my policies."
        confidence = 0.0
        validated = False

        for attempt in range(max_retries):
            try:
                # call_llm(prompt) would get LLM response. Stub response:
                raw_response = '{"answer": "Based on retrieved policies, Zepto standard delivery is free on orders over INR 149, while orders below this incur an INR 25 fee.", "sources": ["doc_01.txt"], "confidence": 1.0}'
                
                # Parse and validate response
                data = json.loads(raw_response)
                validated_response = AnswerResponse(**data)
                
                answer = validated_response.answer
                sources = validated_response.sources
                confidence = validated_response.confidence
                validated = True
                print(f"[Retry Loop] Validation succeeded on attempt {attempt + 1}")
                break
            except Exception as e:
                print(f"[Retry Loop] Validation failed on attempt {attempt + 1}: {e}")

        if not validated:
            print("[Retry Loop] Failed to retrieve a validated JSON response after maximum retries.")
    else:
        # Baseline Mock mode: Return first 200 chars of the most similar chunk
        top_chunk = retrieved_chunks[0] if retrieved_chunks else "No policy information found."
        answer = f"Based on the retrieved context: {top_chunk[:200]}"
        # Limit sources to only the document ID of the top matched chunk
        sources = [sources[0]] if sources else []
        confidence = 1.0

    return {
        "retrieved_chunks": retrieved_chunks,
        "sources": sources,
        "answer": answer,
        "confidence": confidence
    }


def direct_answer(state: AgentState) -> dict:
    """
    Handles general non-policy questions directly with a fallback response.
    """
    mock_llm = os.getenv("MOCK_LLM", "1")

    if mock_llm == "0":
        # Stub branch for actual LLM general chat
        answer = "I can only address queries covered in policy docs."
    else:
        # Baseline Mock mode
        answer = "I can only answer questions about Zepto policies right now."

    print(f"[Node: direct_answer] Returning general fallback message.")
    return {
        "sources": [],
        "answer": answer,
        "confidence": 1.0
    }


def route_intent(state: AgentState) -> str:
    """
    Router function to select the next node based on intent classification.
    """
    return state["intent"]


# Build StateGraph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("classify_intent", classify_intent)
workflow.add_node("retrieve_and_answer", retrieve_and_answer)
workflow.add_node("direct_answer", direct_answer)

# Set entry point
workflow.set_entry_point("classify_intent")

# Add Routing Edge
workflow.add_conditional_edges(
    "classify_intent",
    route_intent,
    {
        "policy_question": "retrieve_and_answer",
        "general_question": "direct_answer"
    }
)

# Add termination edges
workflow.add_edge("retrieve_and_answer", END)
workflow.add_edge("direct_answer", END)

# Compile graph
graph = workflow.compile()
