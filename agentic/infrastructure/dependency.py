from dependency_injector import containers, providers
from typing import Callable
import logging
from agentic.application.repository_interfaces import IHistoryManager
from agentic.application.portal_interface import IPortalApiClient
from agentic.application.service_interface import IChatService
from agentic.infrastructure.memory_history import MemoryHistoryManager
from agentic.infrastructure.portal_api_client import PortalApiClient
from agentic.infrastructure.service.chat_service import ChatService
from agentic.infrastructure.ai_client import OllamaClient

logger = logging.getLogger(__name__)

class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    ai_client = providers.Singleton(OllamaClient)

    portal_client = providers.Singleton(PortalApiClient)

    history_manager: Callable[[], IHistoryManager] = providers.Singleton(MemoryHistoryManager)

    chat_service: Callable[[], IChatService] = providers.Factory(
        ChatService,
        history_manager=history_manager,
        portal_client=portal_client,
        ai_client=ai_client
    )

container = Container()