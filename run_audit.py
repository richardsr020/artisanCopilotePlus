"""
Script principal pour lancer l'audit complet du projet.
"""
import os
from audit_tools.file_auditor import FileAuditor
from audit_tools.scoring import Scoring
from audit_tools.todo_generator import TodoGenerator
from audit_tools.refactoring_suggester import RefactoringSuggester
from audit_tools.robustness_tester import RobustnessTester

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    print("==== Audit automatique du projet ====")
    
    # 1. Découpage & audit fichier par fichier ou par bloc
    MAX_TOKENS = 4000  # Limite de tokens/caractères par bloc (modifiable selon le modèle cible)
    auditor = FileAuditor(PROJECT_ROOT)
    audits = auditor.audit_files(max_tokens=MAX_TOKENS)
    print("\n--- Résumés par fichier (découpage par bloc si besoin) ---")
    for fp, summary in audits.items():
        print(f"{fp}: {summary}")
    print("\n--- Résumé global ---")
    print(auditor.global_summary(audits))

    # 2. Scoring automatique sur tous les fichiers
    scoring = Scoring()
    all_scores = {k: [] for k in scoring.scores.keys()}
    for fp in auditor.file_list:
        with open(fp, 'r', encoding='utf-8') as f:
            code = f.read()
        file_scores = scoring.auto_score(code)
        for k, v in file_scores.items():
            all_scores[k].append(v)
    # Calcul de la moyenne par catégorie
    avg_scores = {k: int(sum(v)/len(v)) if v else 0 for k, v in all_scores.items()}
    print("\n--- Scoring automatique (moyenne par catégorie) ---")
    for k, v in avg_scores.items():
        print(f"{k} : {v}/10")

    # 3. TODO list (analyse automatique)
    todo = TodoGenerator()
    for fp in auditor.file_list:
        with open(fp, 'r', encoding='utf-8') as f:
            code = f.read()
        todo.auto_todos(code, os.path.basename(fp))
    print("\n--- TODO list (analyse automatique) ---")
    print(todo.generate_markdown())

    # 4. Suggestions de refactoring (analyse automatique)
    refactoring = RefactoringSuggester()
    for fp in auditor.file_list:
        with open(fp, 'r', encoding='utf-8') as f:
            code = f.read()
        refactoring.auto_suggestions(code, os.path.basename(fp))
    print("\n--- Suggestions de refactoring (analyse automatique) ---")
    print(refactoring.summary())

    # 5. Test de robustesse (simulation)
    robustness = RobustnessTester()
    for fp in auditor.file_list:
        robustness.test_file(fp)
    print("\n--- Résultats test de robustesse ---")
    print(robustness.report())
