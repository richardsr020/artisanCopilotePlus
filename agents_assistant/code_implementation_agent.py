from .agent_base import AgentBase

import logging
from .agent_base import AgentBase
from core.file_manager import FileManager

class CodeImplementationAgent(AgentBase):
    def __init__(self, name, bus):
        super().__init__(name, bus)
        self.file_manager = FileManager()
        self.logger = logging.getLogger("CodeImplementationAgent")

    async def handle(self, message):
        code = message["payload"].get("code")
        meta = message["payload"].get("meta", {})
        file_path = meta.get("file_path", "generated_code.py")
        try:
            self.logger.info(f"Insertion du code dans {file_path}...")
            # Simule l'écriture et retourne le code généré (pour les tests)
            result = f"Code ajouté dans {file_path} :\n{code}"
            self.logger.info(f"Succès: {result}")
        except Exception as e:
            result = f"[ERREUR] Impossible d'insérer le code : {e}"
            self.logger.error(result)
        await self.send("ConversationMemoryAgent", {"result": result})
