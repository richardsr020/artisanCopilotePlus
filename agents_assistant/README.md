# agents_assistant

Système multi-agents pour l'assistance au développement logiciel.

## Agents principaux
- **NLUAgent** : Interprète les requêtes utilisateur en langage naturel.
- **CodeGenerationAgent** : Génère du code à partir des intentions structurées.
- **CodeImplementationAgent** : Intègre le code généré dans le projet (utilise FileManager).
- **EnvManagementAgent** : Gère l'environnement, l'analyse de structure et les commandes (avec validation utilisateur).
- **ConversationMemoryAgent** : Gère la mémoire, la session, la validation et le dialogue.

## Architecture
- Communication asynchrone via un bus de messages (`MessageBus`).
- Chaque agent est une classe indépendante, extensible et testable.
- Gestion de sessions/contextes multiples possible.

## Extension
Pour ajouter un agent, créez une nouvelle classe héritant de `AgentBase` et enregistrez-la dans le bus.

## Exemple d'utilisation
```python
from core.agent import Agent
agent = Agent()
reponse = agent.traiter_instruction("Crée une fonction foo en python")
print(reponse)
```

## Tests
Vous pouvez injecter des mocks ou des sous-classes d'agents dans le constructeur de `Agent` pour les tests unitaires.

## Logs
Tous les agents utilisent le module `logging` pour des logs structurés.

---
