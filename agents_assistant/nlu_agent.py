from .agent_base import AgentBase
import re
import os
from groq import Groq
from dotenv import load_dotenv

class NLUAgent(AgentBase):
    def translate_to_english(self, text):
        # Placeholder : à remplacer par une vraie API ou lib de traduction
        # Pour l'instant, retourne le texte tel quel
        return text

    async def handle(self, message):
        user_input = message["payload"]["user_input"]
        projet_courant = message["payload"].get("projet")
        # Détection d'intention d'analyse de projet
        if any(mot in user_input.lower() for mot in ["analyse", "structure"]) and projet_courant:
            await self.send("EnvManagementAgent", {"analyse_structure": projet_courant})
            return
        # Sinon, flux IA habituel
        user_input_en = self.translate_to_english(user_input)
        ia_response = await self.call_llm_api(user_input_en)
        await self.send("ConversationMemoryAgent", {"result": ia_response})

    @staticmethod
    def split_into_chunks(text, max_length=4000):
        """
        Découpe le texte en blocs de max_length caractères (remplacer par un découpage token si besoin).
        """
        return [text[i:i+max_length] for i in range(0, len(text), max_length)]

    async def call_llm_api(self, prompt):
        """
        Appel à l'API Groq avec découpage automatique du prompt en blocs pour éviter l'erreur 413.
        """
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "[ERREUR] GROQ_API_KEY manquante dans .env"
        client = Groq(api_key=api_key)
        max_prompt_length = 4000  # Limite de sécurité (caractères). Adapter selon le modèle Groq.
        prompt_chunks = self.split_into_chunks(prompt, max_prompt_length)
        responses = []
        for chunk in prompt_chunks:
            try:
                completion = client.chat.completions.create(
                    model="deepseek-r1-distill-llama-70b",
                    messages=[
                        {"role": "system", "content": "You are an expert software engineer. Always answer as a professional developer, in various programming languages, and focus your answers on programming and software engineering topics.\n\nFormatting rules:\n- Never display your internal reasoning or thinking process to the user, not even in a collapsible block or in any form.\n- Only output the final answer intended for the user, formatted in markdown.\n- Use markdown headings (#, ##, ###), code blocks (```python, ```bash), lists, and other formatting for clarity.\n- Make your answers visually clear and easy to read for a developer."},
                        {"role": "user", "content": chunk}
                    ],
                    temperature=0.6,
                    max_completion_tokens=4096,
                    top_p=0.95,
                    stream=True,
                    stop=None,
                )
                # Récupérer tout le flux et concaténer la réponse
                full_response = ""
                for resp_chunk in completion:
                    full_response += resp_chunk.choices[0].delta.content or ""
                responses.append(full_response.strip())
            except Exception as e:
                responses.append(f"[ERREUR GROQ] {e}")
        return '\n\n'.join(responses)
