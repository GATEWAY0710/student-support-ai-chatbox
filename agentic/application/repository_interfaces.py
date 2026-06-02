from abc import ABC, abstractmethod
from typing import List, Optional
from agentic.domain.request_models import MessageCreate, Message, ChatSession

class IHistoryManager(ABC):
    @abstractmethod
    def create_session(self, session_id: str, title: str) -> ChatSession:
        raise NotImplementedError

    @abstractmethod
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        raise NotImplementedError

    @abstractmethod
    def get_all_sessions(self) -> List[ChatSession]:
        raise NotImplementedError

    @abstractmethod
    def save_message(self, session_id: str, role: str, content: str) -> Message:
        raise NotImplementedError

    @abstractmethod
    def get_history(self, session_id: str, limit: int = 20) -> List[dict]:
        raise NotImplementedError