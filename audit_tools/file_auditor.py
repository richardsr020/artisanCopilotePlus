"""
Module file_auditor.py
Découpage automatique du projet et génération de résumés fichier par fichier.
"""

import os
from typing import List, Dict

class FileAuditor:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.file_list = self._gather_files()

    def _gather_files(self) -> List[str]:
        files = []
        for dirpath, _, filenames in os.walk(self.root_dir):
            for f in filenames:
                if f.endswith('.py'):
                    files.append(os.path.join(dirpath, f))
        return files

    def audit_files(self, max_tokens: int = 8000) -> Dict[str, str]:
        """
        Retourne un dict {filepath: résumé automatique} pour chaque fichier.
        Découpe les fichiers trop longs en blocs de max_tokens (par défaut 8000 caractères).
        """
        audits = {}
        for f in self.file_list:
            with open(f, 'r', encoding='utf-8') as file:
                content = file.read()
            chunks = self.split_file_into_chunks(content, max_tokens)
            chunk_summaries = []
            for i, chunk in enumerate(chunks):
                summary = self.summarize_python_file(chunk, f)
                if len(chunks) > 1:
                    chunk_summaries.append(f"[Bloc {i+1}/{len(chunks)}]\n{summary}")
                else:
                    chunk_summaries.append(summary)
            audits[f] = '\n\n'.join(chunk_summaries)
        return audits

    @staticmethod
    def split_file_into_chunks(content: str, max_tokens: int) -> list:
        """
        Découpe le contenu en blocs de max_tokens (approximé par caractères pour simplicité).
        """
        # Pour une vraie découpe par tokens, utiliser tiktoken ou autre tokenizer LLM si besoin
        return [content[i:i+max_tokens] for i in range(0, len(content), max_tokens)]

    @staticmethod
    def summarize_python_file(content: str, filepath: str) -> str:
        """Génère un résumé automatique du fichier Python."""
        import ast
        try:
            tree = ast.parse(content)
        except Exception as e:
            return f"Impossible d'analyser {os.path.basename(filepath)} : {e}"
        docstring = ast.get_docstring(tree)
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        summary_lines = []
        if docstring:
            summary_lines.append(f"Docstring module : {docstring.strip()}")
        if classes:
            summary_lines.append(f"Classes : {', '.join(c.name for c in classes)}")
            for c in classes:
                doc = ast.get_docstring(c)
                if doc:
                    summary_lines.append(f"  - {c.name} : {doc.strip()}")
        if functions:
            summary_lines.append(f"Fonctions : {', '.join(f.name for f in functions)}")
            for func in functions:
                doc = ast.get_docstring(func)
                if doc:
                    summary_lines.append(f"  - {func.name} : {doc.strip()}")
        if not (docstring or classes or functions):
            summary_lines.append("Pas de docstring, classe ou fonction détectée.")
        return '\n'.join(summary_lines)

    def global_summary(self, audits: Dict[str, str]) -> str:
        """Génère un résumé global à partir des résumés fichiers."""
        return '\n'.join([f"- {os.path.basename(fp)}: {summary}" for fp, summary in audits.items()])
