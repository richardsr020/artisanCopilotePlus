"""
Module todo_generator.py
Génération automatique de TODO list à partir des recommandations.
"""
from typing import List

class TodoGenerator:
    def __init__(self):
        self.todos = []

    def add_todo(self, recommendation: str):
        self.todos.append(recommendation)

    def auto_todos(self, code: str, filename: str = ""):
        """Analyse le code et ajoute des TODO pour patterns courants."""
        import ast
        try:
            tree = ast.parse(code)
        except Exception:
            self.add_todo(f"{filename}: Fichier non analysable")
            return
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Docstring absente
                if not ast.get_docstring(node):
                    self.add_todo(f"{filename}: Ajouter une docstring à la fonction '{node.name}'")
                # Fonction trop longue
                if hasattr(node, 'body') and len(node.body) > 30:
                    self.add_todo(f"{filename}: Découper la fonction '{node.name}' (>30 lignes)")
                # Trop de paramètres
                if hasattr(node, 'args') and hasattr(node.args, 'args') and len(node.args.args) > 5:
                    self.add_todo(f"{filename}: Réduire le nombre de paramètres de '{node.name}' (>5)")
            if isinstance(node, ast.Module):
                # Absence de gestion d'erreur
                has_try = any(isinstance(n, ast.Try) for n in ast.walk(node))
                if not has_try:
                    self.add_todo(f"{filename}: Ajouter gestion d'erreur (try/except)")

    def generate_markdown(self) -> str:
        return '\n'.join([f"- [ ] {todo}" for todo in self.todos])
