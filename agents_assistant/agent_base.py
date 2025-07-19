import asyncio
from typing import Any, Dict

class AgentBase:
    def __init__(self, name: str, bus: "MessageBus"):
        self.name = name
        self.bus = bus

    async def handle(self, message: Dict[str, Any]):
        """Override in subclass: handle incoming message"""
        raise NotImplementedError

    async def send(self, recipient: str, payload: Dict[str, Any]):
        await self.bus.send(self.name, recipient, payload)
