import asyncio
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter(prefix="/aria", tags=["ARIA"])

class Message(BaseModel):
    role: str
    content: str
    
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    history: List[Message] = []

@router.post("/chat")
async def aria_chat(request: ChatRequest):
    """
    JSON endpoint for ARIA chatbot.
    Returns a structured response with the AI-generated message.
    """
    from app.services.aria_service import get_aria_response
    
    response_text = await get_aria_response(request.message, request.history)
    
    return {
        "response": response_text,
        "mode": "intelligence",
        "status": "complete"
    }

@router.post("/chat/stream")
async def aria_chat_stream(request: ChatRequest):
    """
    Streaming SSE endpoint for ARIA chatbot (for advanced clients).
    """
    from app.services.aria_service import generate_aria_response
    
    return StreamingResponse(
        generate_aria_response(request.message, request.history),
        media_type="text/event-stream"
    )

@router.get("/conversations")
async def get_conversations():
    """Mock endpoint to return conversation history list."""
    return []

@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Mock endpoint to return specific conversation history."""
    return {"id": conversation_id, "messages": []}
