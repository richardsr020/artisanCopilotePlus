import sys
import asyncio
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "agents_assistant"))

from agents_assistant import (
    NLUAgent, CodeGenerationAgent, CodeImplementationAgent,
    EnvManagementAgent, ConversationMemoryAgent, MessageBus
)

def build_agents(bus):
    return [
        NLUAgent("NLUAgent", bus),
        CodeGenerationAgent("CodeGenerationAgent", bus),
        CodeImplementationAgent("CodeImplementationAgent", bus),
        EnvManagementAgent("EnvManagementAgent", bus),
        ConversationMemoryAgent("ConversationMemoryAgent", bus),
    ]

async def main():
    bus = MessageBus()
    agents = build_agents(bus)
    for agent in agents:
        bus.register_agent(agent)

    # Exemple : simuler une requête utilisateur
    await bus.send("user", "NLUAgent", {"user_input": "Crée une fonction foo en python"})
    await bus.start()

if __name__ == "__main__":
    asyncio.run(main())
