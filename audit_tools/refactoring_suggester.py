"""
Module refactoring_suggester.py
Suggestions de refactoring modulaire.
"""
from typing import List

class RefactoringSuggester:
    def __init__(self):
        self.suggestions = []

    def add_suggestion(self, suggestion: str):
        self.suggestions.append(suggestion)

    def auto_suggestions(self, code: str, filename: str = ""):
        """Analyse le code et ajoute des suggestions de refactoring."""
        import ast
        try:
            tree = ast.parse(code)
        except Exception:
            self.add_suggestion(f"{filename}: Fichier non analysable pour refactoring")
            return
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if hasattr(node, 'body') and len(node.body) > 50:
                    self.add_suggestion(f"{filename}: Découper la fonction '{node.name}' (>50 lignes)")
                # Fonctions imbriquées
                for subnode in node.body:
                    if isinstance(subnode, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        self.add_suggestion(f"{filename}: Éviter les fonctions imbriquées dans '{node.name}'")
            if isinstance(node, ast.ClassDef):
                if hasattr(node, 'body') and len(node.body) > 50:
                    self.add_suggestion(f"{filename}: Découper la classe '{node.name}' (trop de méthodes)")
        # Classe monolithique (fichier trop long)
        if code.count('\n') > 500:
            self.add_suggestion(f"{filename}: Découper le fichier (plus de 500 lignes)")

    def summary(self) -> str:
        return '\n'.join([f"- {s}" for s in self.suggestions])
