import unittest
from core.agent import Agent

class TestAgentSystem(unittest.TestCase):
    def setUp(self):
        self.agent = Agent()

    def tearDown(self):
        self.agent.close()

    def test_simple_code_generation(self):
        response = self.agent.traiter_instruction("Crée une fonction foo en python")
        self.assertIn("foo", response)
        self.assertIn("python", response.lower() or "py" in response.lower())

    def test_session_memory(self):
        self.agent.traiter_instruction("Crée une fonction bar en python")
        # On vérifie que la mémoire a bien été alimentée (via ConversationMemoryAgent)
        mem = self.agent.conv_agent.memory.get_context(n=2)
        self.assertTrue(any("bar" in str(x) for x in mem))

if __name__ == "__main__":
    unittest.main()
