"""
agent.py
Handles the AI processing logic for artisanCopilotePlus.
"""

import asyncio
from agents_assistant import (
    NLUAgent, CodeGenerationAgent, CodeImplementationAgent,
    EnvManagementAgent, ConversationMemoryAgent, MessageBus
)

class Agent:
    """
    Orchestrateur central du système multi-agents pour artisanCopilotePlus.
    Toutes les requêtes utilisateur transitent par ce bus d'agents spécialisés.
    """
    def __init__(self, nlu_agent_cls=NLUAgent, code_gen_agent_cls=CodeGenerationAgent,
                 code_impl_agent_cls=CodeImplementationAgent, env_agent_cls=EnvManagementAgent,
                 conv_agent_cls=ConversationMemoryAgent):
        # Boucle événementielle robuste (pour compatibilité thread/tests)
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        self.bus = MessageBus()
        self._response = None
        self._response_event = asyncio.Event()
        # Instanciation des agents (permet l'injection pour tests ou extension)
        self.nlu_agent = nlu_agent_cls("NLUAgent", self.bus)
        self.code_gen_agent = code_gen_agent_cls("CodeGenerationAgent", self.bus)
        self.code_impl_agent = code_impl_agent_cls("CodeImplementationAgent", self.bus)
        self.env_agent = env_agent_cls("EnvManagementAgent", self.bus)
        self.conv_agent = conv_agent_cls("ConversationMemoryAgent", self.bus)
        # Callback pour synchronisation réponse
        self.conv_agent._external_callback = self._set_response
        for agent in [self.nlu_agent, self.code_gen_agent, self.code_impl_agent, self.env_agent, self.conv_agent]:
            self.bus.register_agent(agent)
        # Démarrer la boucle agents (en tâche de fond)
        self._bus_task = self.loop.create_task(self.bus.start())

    def _set_response(self, response):
        self._response = response
        self._response_event.set()

    def traiter_instruction(self, instruction: str, projet_courant: str = None, projets_ouverts: list = None) -> str:
        """
        Envoie l'instruction utilisateur dans le bus multi-agents et attend la réponse finale du ConversationMemoryAgent.
        """
        async def agent_query():
            self._response = None
            self._response_event.clear()
            await self.bus.send("user", "NLUAgent", {"user_input": instruction, "user": "test", "projet": projet_courant or "default"})
            await self._response_event.wait()
            return self._response
        try:
            return self.loop.run_until_complete(agent_query())
        except Exception as e:
            return f"[ERREUR IA] {e}"

    def close(self):
        """Arrête proprement la boucle des agents (pour tests ou arrêt logiciel)."""
        if self._bus_task:
            self._bus_task.cancel()
        try:
            self.loop.stop()
        except Exception:
            pass