from datetime import datetime
from typing import List, Optional, Dict
from agentic.application.repository_interfaces import IHistoryManager
from agentic.domain.request_models import Message, ChatSession

class MemoryHistoryManager(IHistoryManager):
    def __init__(self):
        # session_id -> ChatSession
        self._sessions: Dict[str, ChatSession] = {}

    def create_session(self, session_id: str, title: str = "New Chat") -> ChatSession:
        session = ChatSession(
            id=0, # Not used for identity in memory
            title=title,
            created_at=datetime.now(),
            messages=[]
        )
        self._sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self._sessions.get(session_id)

    def get_all_sessions(self) -> List[ChatSession]:
        return list(self._sessions.values())

    def save_message(self, session_id: str, role: str, content: str) -> Message:
        if session_id not in self._sessions:
            self.create_session(session_id)
        
        session = self._sessions[session_id]
        message = Message(
            id=len(session.messages) + 1,
            role=role,
            content=content,
            created_at=datetime.now()
        )
        session.messages.append(message)
        return message

    def get_history(self, session_id: str, limit: int = 10) -> List[dict]:
        session = self._sessions.get(session_id)
        if not session:
            return []
        
        # Return last N messages in the format expected by OllamaClient
        history = [{"role": m.role, "content": m.content} for m in session.messages]
        return history[-limit:]
