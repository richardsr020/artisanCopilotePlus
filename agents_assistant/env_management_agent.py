from .agent_base import AgentBase

import logging
import os
from .agent_base import AgentBase
from core.file_manager import FileManager

class EnvManagementAgent(AgentBase):
    def __init__(self, name, bus):
        super().__init__(name, bus)
        self.logger = logging.getLogger("EnvManagementAgent")
        self.file_manager = FileManager()

    async def handle(self, message):
        command = message["payload"].get("command")
        analyse = message["payload"].get("analyse_structure")
        if command:
            self.logger.info(f"Demande de validation utilisateur pour la commande : {command}")
            await self.send("ConversationMemoryAgent", {"ask_validation": command})
        if analyse:
            # 1. Analyse brute de la structure du projet
            structure = self._analyser_structure(analyse)
            # 2. Audit complet de chaque fichier code du projet
            try:
                from agents_assistant.nlu_agent import NLUAgent
                nlu = NLUAgent("NLUAgent", self.bus)
                # Rapport général projet
                prompt_proj = (
                    "Voici la structure d'un projet logiciel :\n" + structure +
                    "\n\nAnalyse ce projet de façon professionnelle. Déduis le type de projet, les technologies, le langage, le framework, les fichiers clés, et produis un rapport markdown détaillé pour un développeur :\n" +
                    "- Résumé\n- Langages et frameworks\n- Fichiers importants\n- Type de projet\n- Conseils ou remarques éventuelles."
                )
                rapport_global = await nlu.call_llm_api(prompt_proj)
                # Audit de chaque fichier code
                import pathlib
                import asyncio
                rapport_fichiers = []
                exclude_dirs = [
                    '/venv/', '/env/', '/.env/', '/.venv/', '/node_modules/', '/.git/', '/__pycache__/', '/site-packages/'
                ]
                for fichier in structure.splitlines():
                    # Exclure les dépendances et dossiers système
                    if any(ex in fichier for ex in exclude_dirs):
                        continue
                    ext = pathlib.Path(fichier).suffix.lower()
                    if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.cs', '.go', '.rb', '.php', '.sh']:
                        try:
                            with open(fichier, 'r', encoding='utf-8', errors='ignore') as f:
                                contenu = f.read()
                            prompt_audit = (
                                f"Voici le contenu du fichier '{fichier}':\n" + contenu +
                                "\n\nFais un audit professionnel de ce fichier code. Analyse les aspects suivants :\n- Sécurité\n- Performance\n- Efficacité\n- Suggestions d'amélioration\n- Bonnes pratiques\nDonne un rapport markdown détaillé pour ce fichier."
                            )
                            audit = await nlu.call_llm_api(prompt_audit)
                            rapport_fichiers.append(f"## Audit du fichier `{fichier}`\n" + audit)
                        except Exception as e:
                            rapport_fichiers.append(f"## Audit du fichier `{fichier}`\n[ERREUR lecture] {e}")
                rapport_final = rapport_global + "\n\n" + "\n\n".join(rapport_fichiers)
                await self.send("ConversationMemoryAgent", {"result": rapport_final})
            except Exception as e:
                await self.send("ConversationMemoryAgent", {"result": structure + f"\n[ERREUR analyse IA] {e}"})

    def _analyser_structure(self, path):
        try:
            fichiers = []
            for root, dirs, files in os.walk(path):
                for name in files:
                    fichiers.append(os.path.join(root, name))
            return f"Structure du projet :\n" + "\n".join(fichiers)
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de structure : {e}")
            return f"[ERREUR] {e}"
