from typing import Dict, Any, List

class Memory:
    def __init__(self):
        self.history: List[Dict[str, Any]] = []

    def add(self, entry: Dict[str, Any]):
        self.history.append(entry)

    def get_context(self, n=5):
        return self.history[-n:]
