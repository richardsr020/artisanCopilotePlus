"""
Module scoring.py
Gestion du scoring par catégorie (Sécurité, Performance, Efficacité, Bonnes Pratiques).
"""

from typing import Dict

class Scoring:
    def __init__(self):
        self.scores = {
            'Sécurité': 0,
            'Performance': 0,
            'Efficacité': 0,
            'Bonnes Pratiques': 0
        }

    def set_score(self, category: str, score: int):
        if category in self.scores:
            self.scores[category] = min(max(score, 0), 10)

    def get_scores(self) -> Dict[str, int]:
        return self.scores

    def summary(self) -> str:
        return '\n'.join([f"{cat} : {score}/10" for cat, score in self.scores.items()])

    def auto_score(self, code: str) -> Dict[str, int]:
        """
        Analyse le code source et attribue un score objectif pour chaque catégorie.
        """
        import ast
        try:
            tree = ast.parse(code)
        except Exception:
            return {k: 0 for k in self.scores}
        # Sécurité : try/except, input validation, gestion d'erreurs
        nb_try = len([n for n in ast.walk(tree) if isinstance(n, ast.Try)])
        nb_assert = len([n for n in ast.walk(tree) if isinstance(n, ast.Assert)])
        nb_raise = len([n for n in ast.walk(tree) if isinstance(n, ast.Raise)])
        security_score = min(2 * nb_try + nb_assert + nb_raise, 10)
        # Performance : list/set/dict comprehensions, pas de boucle inutile
        nb_comprehensions = len([n for n in ast.walk(tree) if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp))])
        nb_loops = len([n for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While))])
        perf_score = min(3 * nb_comprehensions + max(0, 5 - nb_loops), 10)
        # Efficacité : nombre de fonctions/classes, modularité
        nb_func = len([n for n in tree.body if isinstance(n, ast.FunctionDef)])
        nb_class = len([n for n in tree.body if isinstance(n, ast.ClassDef)])
        eff_score = min(nb_func + 2 * nb_class, 10)
        # Bonnes pratiques : docstrings, annotations, nommage
        nb_doc = sum([
            1 for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and ast.get_docstring(n)
        ])
        nb_ann = len([n for n in ast.walk(tree) if isinstance(n, ast.AnnAssign)])
        nb_typing = len([n for n in ast.walk(tree) if hasattr(n, 'annotation') and n.annotation is not None])
        good_score = min(nb_doc + nb_ann + nb_typing, 10)
        scores = {
            'Sécurité': security_score,
            'Performance': perf_score,
            'Efficacité': eff_score,
            'Bonnes Pratiques': good_score
        }
        self.scores = scores
        return scores
