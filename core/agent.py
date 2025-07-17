"""
agent.py
Gère la logique de traitement IA pour artisanCopilotePlus.
"""

import os

from .file_manager import FileManager

class Agent:
    def __init__(self):
        try:
            from groq import Groq
        except ImportError:
            raise ImportError("Le module 'groq' n'est pas installé. Ajoutez-le dans requirements.txt et installez-le manuellement.")
        # Charger la clé API depuis un .env si python-dotenv est disponible
        if not os.environ.get("GROQ_API_KEY"):
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass  # python-dotenv n'est pas obligatoire, on continue
        self.api_key = os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("La clé API Groq n'est pas définie. Ajoutez GROQ_API_KEY=... dans un fichier .env à la racine du projet ou exportez-la dans l'environnement.")
        self.client = Groq(api_key=self.api_key)
        self.system_prompt = "Vous êtes un assistant IA pour développeur. Répondez de façon concise et utile."

    def traiter_instruction(self, instruction: str, projet_courant: str = None, projets_ouverts: list = None) -> str:
        """
        Traite l'instruction utilisateur. Si l'instruction demande une opération sur le système de fichiers
        (création, suppression, modification, renommage de fichiers/dossiers), exécute l'action sur tous
        les dossiers de projets ouverts (projets_ouverts). Sinon, comportement IA classique.
        """
        try:
            # Gestion CRUD sur tous les projets ouverts
            if projets_ouverts and self._instruction_est_crud(instruction):
                return self._executer_instruction_crud(instruction, projets_ouverts)

            # Si l'utilisateur demande d'analyser le projet courant
            if projet_courant and any(mot in instruction.lower() for mot in ["analyse", "analyser", "décris", "décrire", "explique", "présente", "structure", "résume"]):
                context = self._generer_resume_projet(projet_courant)
                prompt = (
                    f"Voici le contenu principal du projet sélectionné :\n{context}\n"
                    f"Analyse ce projet et explique à l'utilisateur de quoi il s'agit, ses fonctionnalités, sa structure,et tout ce que tu peux en déduire. tu peu suggerer des ameliorations si tu as des suggestions d'améliorations, indique les dans un bloc markdown dans ton analyse si le dossier est vide, indique que le dossier est vide"
                )
            else:
                prompt = instruction
            # Utilisation du modèle deepseek avec streaming
            completion = self.client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_completion_tokens=4096,
                top_p=0.95,
                stream=True,
                stop=None
            )
            # Concaténer la réponse au fur et à mesure
            full_response = ""
            for chunk in completion:
                content = getattr(chunk.choices[0].delta, "content", None)
                if content:
                    full_response += content
            return full_response.strip() if full_response else "[ERREUR IA] Réponse vide."
        except Exception as e:
            return f"[ERREUR IA] {str(e)}"

            completion = self.client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_completion_tokens=4096,
                top_p=0.95,
                stream=True,
                stop=None
            )
            # Concaténer la réponse au fur et à mesure
            full_response = ""
            for chunk in completion:
                content = getattr(chunk.choices[0].delta, "content", None)
                if content:
                    full_response += content
            return full_response.strip() if full_response else "[ERREUR IA] Réponse vide."
        except Exception as e:
            return f"[ERREUR IA] {str(e)}"

    def _instruction_est_crud(self, instruction: str) -> bool:
        mots_crud = [
            "crée", "créer", "cree", "cree", "ajoute", "ajouter", "supprime", "supprimer", "efface", "effacer",
            "modifie", "modifier", "renomme", "renommer", "déplace", "deplacer", "déplacer", "déplacer",
            "écris", "écrire", "write", "delete", "remove", "move", "rename", "mkdir", "touch", "edit"
        ]
        return any(mot in instruction.lower() for mot in mots_crud)

    def _executer_instruction_crud(self, instruction: str, projets_ouverts: list) -> str:
        """
        Exécute l'instruction CRUD sur tous les dossiers de projets ouverts.
        """
        fm = FileManager()
        reponses = []
        import re
        # Création de fichier
        match = re.match(r".*cr[ée]e?r? un fichier ([^ ]+)(?: dans ([^ ]+))?(?: avec (.*))?", instruction, re.IGNORECASE)
        if match:
            nom_fichier, dossier, contenu = match.groups()
            for projet in projets_ouverts:
                base = dossier if dossier else projet
                chemin = os.path.join(base, nom_fichier)
                reponses.append(fm.creer_fichier(chemin, contenu or ""))
            return "\n".join(reponses)
        # Création de dossier
        match = re.match(r".*cr[ée]e?r? un dossier ([^ ]+)(?: dans ([^ ]+))?", instruction, re.IGNORECASE)
        if match:
            nom_dossier, dossier = match.groups()
            for projet in projets_ouverts:
                base = dossier if dossier else projet
                chemin = os.path.join(base, nom_dossier)
                reponses.append(fm.creer_dossier(chemin))
            return "\n".join(reponses)
        # Suppression
        match = re.match(r".*supprime(r)? (le fichier|le dossier|le répertoire)? ([^ ]+)", instruction, re.IGNORECASE)
        if match:
            _, type_cible, cible = match.groups()
            for projet in projets_ouverts:
                chemin = os.path.join(projet, cible)
                reponses.append(fm.supprimer(chemin))
            return "\n".join(reponses)
        # Par défaut, message d'erreur
        return "[ERREUR] Impossible de comprendre l'opération CRUD demandée. Soyez plus explicite (ex: crée un fichier test.py dans monprojet)."


    def _generer_resume_projet(self, dossier: str) -> str:
        """ Génère un résumé textuel du projet : structure, README, principaux fichiers. """
        resume = f"Structure du dossier {os.path.basename(dossier)}:\n"
        for root, dirs, files in os.walk(dossier):
            # Limiter la profondeur et le nombre de fichiers pour éviter les prompts trop longs
            rel_root = os.path.relpath(root, dossier)
            if rel_root == ".":
                rel_root = ""
            for d in dirs:
                resume += f"- [dossier] {os.path.join(rel_root, d)}\n"
            for f in files:
                path = os.path.join(root, f)
                resume += f"- [fichier] {os.path.join(rel_root, f)}\n"
        # Lire README.md si présent
        readme_path = os.path.join(dossier, "README.md")
        if os.path.isfile(readme_path):
            try:
                with open(readme_path, "r", encoding="utf-8") as f:
                    contenu = f.read(1500)
                    resume += f"\nExtrait du README.md :\n{contenu}\n"
            except Exception:
                pass
        # Lire les 2-3 premiers fichiers .py
        py_files = [os.path.join(root, f) for root, _, files in os.walk(dossier) for f in files if f.endswith('.py')][:3]
        for pyf in py_files:
            try:
                with open(pyf, "r", encoding="utf-8") as f:
                    code = f.read(800)
                    resume += f"\nExtrait de {os.path.relpath(pyf, dossier)} :\n" + code + "\n"
            except Exception:
                pass
        return resume[:3500]
