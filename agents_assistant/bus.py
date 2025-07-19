import asyncio
from typing import Dict, Any

class MessageBus:
    def __init__(self):
        self.queues = {}
        self.agents = {}

    def register_agent(self, agent):
        self.queues[agent.name] = asyncio.Queue()
        self.agents[agent.name] = agent

    async def send(self, sender: str, recipient: str, payload: Dict[str, Any]):
        message = {"from": sender, "to": recipient, "payload": payload}
        await self.queues[recipient].put(message)

    async def start(self):
        tasks = []
        for name, agent in self.agents.items():
            tasks.append(asyncio.create_task(self._agent_loop(agent)))
        await asyncio.gather(*tasks)

    async def _agent_loop(self, agent):
        queue = self.queues[agent.name]
        while True:
            message = await queue.get()
            await agent.handle(message)
