from .agent_base import AgentBase
from .memory import Memory

import logging
from .agent_base import AgentBase
from .memory import Memory

class ConversationMemoryAgent(AgentBase):
    def __init__(self, name, bus):
        super().__init__(name, bus)
        self.memory = Memory()
        self._external_callback = None  # Pour synchronisation avec Agent principal
        self.logger = logging.getLogger("ConversationMemoryAgent")
        self.sessions = {}  # contextes multiples par user/projet

    async def handle(self, message):
        user = message["payload"].get("user", "default")
        projet = message["payload"].get("projet", "default")
        session_key = (user, projet)
        if session_key not in self.sessions:
            self.sessions[session_key] = []
        result = message["payload"].get("result")
        ask_validation = message["payload"].get("ask_validation")
        if result:
            self.memory.add({"result": result, "user": user, "projet": projet})
            self.sessions[session_key].append(result)
            self.logger.info(f"[Session {session_key}] Réponse : {result}")
            print(f"[ASSISTANT][{user}|{projet}] {result}")
            if self._external_callback:
                self._external_callback(result)
        elif ask_validation:
            # Ici, on pourrait brancher sur une UI ou un callback utilisateur
            self.logger.info(f"[Session {session_key}] Validation requise pour : {ask_validation}")
            # Pas de réponse préenregistrée ni de validation automatique
            return
