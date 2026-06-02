from typing import List, AsyncGenerator
from agentic.application.repository_interfaces import IHistoryManager
from agentic.application.portal_interface import IPortalApiClient
from agentic.application.service_interface import IChatService
from agentic.domain.request_models import ChatSession
from agentic.infrastructure.ai_client import OllamaClient
import logging

logger = logging.getLogger(__name__)

class ChatService(IChatService):
    def __init__(self, history_manager: IHistoryManager, portal_client: IPortalApiClient, ai_client: OllamaClient):
        self.history_manager = history_manager
        self.portal_client = portal_client
        self.ai_client = ai_client

    async def handle_user_message(self, session_id: str, student_id: str, user_message: str) -> str:
        full_response = ""
        async for chunk in self.handle_user_message_stream(session_id, student_id, user_message):
            full_response += chunk
        return full_response

    async def handle_user_message_stream(self, session_id: str, student_id: str, user_message: str) -> AsyncGenerator[str, None]:
        # 1. Get history from Memory History Manager
        history = self.history_manager.get_history(session_id)

        # 2. Save User Message to History
        self.history_manager.save_message(session_id, role="user", content=user_message)

        # 3. Stream AI Response
        full_ai_response = ""
        print(f"DEBUG: Starting stream for session {session_id}")
        async for chunk in self.ai_client.generate_response_stream(
            history, 
            user_message, 
            portal_client=self.portal_client,
            student_id=student_id
        ):
            full_ai_response += chunk
            yield chunk

        print(f"DEBUG: Stream finished. Total length: {len(full_ai_response)}")

        # 4. Save the FULL AI Response to History after streaming is done
        if full_ai_response:
            self.history_manager.save_message(session_id, role="assistant", content=full_ai_response)

    async def create_new_chat(self, session_id: str, title: str = "New Chat") -> ChatSession:
        return self.history_manager.create_session(session_id, title)

    async def list_chats(self) -> List[ChatSession]:
        return self.history_manager.get_all_sessions()