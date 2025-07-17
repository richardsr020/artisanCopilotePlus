"""
Entrée principale du projet artisanCopilotePlus
Ce projet est généré automatiquement à partir d'une description en langage naturel.

Contraintes :
- Pas de serveur web
- Pas de base de données
- Pas d'authentification
- Pas d'installation automatique de dépendances
"""

def main():
    from PyQt5.QtWidgets import QApplication
    import sys
    from ui.chat_window import ChatWindow
    app = QApplication(sys.argv)
    win = ChatWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
