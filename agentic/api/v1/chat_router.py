from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.responses import StreamingResponse
from agentic.infrastructure.dependency import container
from agentic.application.service_interface import IChatService
import uuid

router = APIRouter()

@router.post("")
async def create_session(title: str = "New Chat"):
    chat_service: IChatService = container.chat_service()
    session_id = str(uuid.uuid4())
    await chat_service.create_new_chat(session_id, title)
    return {"session_id": session_id, "title": title}

@router.get("/sessions")
async def list_sessions():
    chat_service: IChatService = container.chat_service()
    return await chat_service.list_chats()

@router.post("/{session_id}/message")
async def send_message(
    session_id: str, 
    message: str, 
    x_student_id: str = Header(..., description="The authenticated student identity from the portal")
):
    chat_service: IChatService = container.chat_service()

    # Return a stream instead of a JSON response
    return StreamingResponse(
        chat_service.handle_user_message_stream(session_id, x_student_id, message),
        media_type="text/plain"
    )