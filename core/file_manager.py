"""
file_manager.py
Gère la création, modification et suppression de fichiers et dossiers.
"""

import os

class FileManager:
    def creer_dossier(self, chemin):
        os.makedirs(chemin, exist_ok=True)
        return f"📁 Création du dossier {chemin}/"

    def creer_fichier(self, chemin, contenu=""):
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(contenu)
        return f"📄 Création de {chemin}"

    def supprimer(self, chemin):
        if os.path.isdir(chemin):
            os.rmdir(chemin)
            return f"🧹 Suppression du dossier {chemin}/"
        elif os.path.isfile(chemin):
            os.remove(chemin)
            return f"🧹 Suppression du fichier {chemin}"
        else:
            return f"❌ Chemin introuvable : {chemin}"
