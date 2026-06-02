from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class IPortalApiClient(ABC):
    @abstractmethod
    async def get_profile(self, token: str) -> Dict[str, Any]:
        """/students/profile"""
        raise NotImplementedError

    @abstractmethod
    async def get_dashboard(self, token: str) -> Dict[str, Any]:
        """/students/dashboard"""
        raise NotImplementedError

    @abstractmethod
    async def get_ledger(self, token: str) -> Dict[str, Any]:
        """/students/my-ledger"""
        raise NotImplementedError
