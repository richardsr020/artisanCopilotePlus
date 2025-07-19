"""
chat_window.py
Interface graphique PyQt5 pour la chatbox artisanCopilotePlus.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QApplication,
    QListWidget, QListWidgetItem, QSplitter, QLabel, QTreeWidget, QTreeWidgetItem, QMenu
)
from PyQt5.QtCore import Qt
import sys
import os

class ChatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧠 ArtisanCopilotePlus")
        self.resize(900, 600)
        self.setMinimumSize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background: #181c24;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 15px;
                color: #e5e9f0;
            }
            QTextEdit, QLineEdit {
                background: #232837;
                border-radius: 8px;
                border: 1px solid #2a2f3b;
                padding: 7px;
                color: #e5e9f0;
            }
            QTextEdit {
                padding: 10px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4f8cff, stop:1 #6bc1ff);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3579e2, stop:1 #4fb8e6);
            }
            QLineEdit {
                margin-right: 8px;
            }
            QListWidget {
                background: #232837;
                border: none;
                border-radius: 0;
                font-size: 14px;
                padding: 8px 0 8px 0;
                color: #e5e9f0;
            }
            QListWidget::item {
                padding: 5px 10px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background: #4f8cff;
                color: white;
            }
            QTreeWidget {
                background: #232837;
                color: #e5e9f0;
                border: none;
                font-size: 13px;
            }
            QLabel {
                color: #8fb3ff;
            }
        """)
        # Splitter horizontal (sidebar + chat)
        self.splitter = QSplitter(Qt.Horizontal)
        # --- Sidebar (liste des dossiers projets)
        self.sidebar = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar.setLayout(self.sidebar_layout)
        self.sidebar.setMaximumWidth(230)
        self.sidebar_label = QLabel("<b>Projets</b>")
        self.sidebar_label.setStyleSheet("padding:8px 0 2px 8px;color:#4f8cff;")
        self.project_list = QListWidget()
        self.project_list.itemSelectionChanged.connect(self.selectionner_projet)
        self.add_project_btn = QPushButton("+ Ajouter dossier…")
        self.add_project_btn.clicked.connect(self.ajouter_dossier_projet)
        self.add_project_btn.setStyleSheet("margin:10px 8px 0 8px;")
        self.sidebar_layout.addWidget(self.sidebar_label)
        self.sidebar_layout.addWidget(self.project_list, 2)
        # Arborescence fichiers
        self.files_label = QLabel("<span style='color:#8fb3ff;'>Fichiers du projet</span>")
        self.files_label.setStyleSheet("padding:4px 0 0 8px;color:#8fb3ff;")
        self.files_tree = QTreeWidget()
        self.files_tree.setHeaderHidden(True)
        self.files_tree.setStyleSheet("background:#181c24;color:#e5e9f0;border:none;font-size:13px;selection-background-color:#26304a;")
        self.sidebar_layout.addWidget(self.files_label)
        self.sidebar_layout.addWidget(self.files_tree, 8)
        self.sidebar_layout.addWidget(self.add_project_btn)
        self.sidebar_layout.addStretch()
        # --- Chat principal (vertical)
        self.main_widget = QWidget()
        self.layout = QVBoxLayout()
        # Barre de titre stylée
        self.title = QTextEdit()
        self.title.setReadOnly(True)
        self.title.setMaximumHeight(38)
        self.title.setText("<h2 style='color:#8fb3ff; margin:0;'>🧠 ArtisanCopilotePlus</h2>")
        self.title.setStyleSheet("background:transparent; border:none; padding-bottom:0px;color:#8fb3ff;")
        # Historique de chat
        # Utiliser QTextBrowser pour permettre les liens cliquables
        from PyQt5.QtWidgets import QTextBrowser
        self.history = QTextBrowser()
        self.history.setReadOnly(True)
        self.history.setStyleSheet("margin-bottom:10px;")
        # Champ de saisie
        self.input = QLineEdit()
        self.input.setPlaceholderText("Écrivez une instruction...")
        self.input.returnPressed.connect(self.envoyer_message)
        # Boutons
        self.send_btn = QPushButton("Envoyer")
        self.send_btn.clicked.connect(self.envoyer_message)
        self.menu_btn = QPushButton("Ouvrir fichier…")
        self.menu_btn.clicked.connect(self.ouvrir_fichier)
        # Layouts
        hbox = QHBoxLayout()
        hbox.addWidget(self.input, 4)
        hbox.addWidget(self.send_btn, 1)
        menu_hbox = QHBoxLayout()
        menu_hbox.addWidget(self.menu_btn)
        menu_hbox.addStretch()
        self.layout.addWidget(self.title)
        self.layout.addWidget(self.history, 10)
        self.layout.addLayout(hbox)
        self.layout.addLayout(menu_hbox)
        self.main_widget.setLayout(self.layout)
        # Splitter placement
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.main_widget)
        self.splitter.setSizes([200, 700])
        # Layout principal
        principal_layout = QVBoxLayout()
        principal_layout.addWidget(self.splitter)
        self.setLayout(principal_layout)
        # Agent IA unique pour la session
        from core.agent import Agent
        self.agent = Agent()
        self.history.append("<i style='color:#888;'>Bienvenue dans <b>ArtisanCopilotePlus</b> ! Donnez une instruction pour commencer.</i>")
        # Liste des projets sélectionnés (paths)
        self.projets = []
        self.projet_courant = None
        # Pour gestion des liens Copy/Run
        self._last_code_blocks = []
        # self.history.setOpenExternalLinks(False)  # QTextEdit n'a pas cette méthode
        self.history.anchorClicked.connect(self._handle_anchor_click)

    def ouvrir_fichier(self):
        # Ouvre une boîte de dialogue pour choisir un fichier à ouvrir (placeholder)
        QFileDialog.getOpenFileName(self, "Ouvrir un fichier")

    def ajouter_dossier_projet(self):
        chemin = QFileDialog.getExistingDirectory(self, "Sélectionner un dossier de projet")
        if chemin and chemin not in self.projets:
            self.projets.append(chemin)
            item = QListWidgetItem("📁 " + os.path.basename(chemin))
            item.setToolTip(chemin)
            item.setData(Qt.UserRole, chemin)
            self.project_list.addItem(item)
            self.project_list.setCurrentItem(item)

    def contextMenuEvent(self, event):
        # Menu contextuel pour supprimer un projet
        pos = self.project_list.mapFrom(self, event.globalPos())
        item = self.project_list.itemAt(pos)
        if item:
            menu = QMenu(self)
            remove_action = menu.addAction("Supprimer ce projet")
            action = menu.exec_(event.globalPos())
            if action == remove_action:
                chemin = item.data(Qt.UserRole)
                idx = self.project_list.row(item)
                self.project_list.takeItem(idx)
                if chemin in self.projets:
                    self.projets.remove(chemin)
                self.files_tree.clear()
                self.projet_courant = None

    def mousePressEvent(self, event):
        # Pour menu contextuel sur la liste des projets
        if event.button() == Qt.RightButton:
            self.contextMenuEvent(event)
        super().mousePressEvent(event)

    def selectionner_projet(self):
        item = self.project_list.currentItem()
        if item:
            chemin = item.data(Qt.UserRole)
            self.projet_courant = chemin
            self.history.append(f"<div style='color:#4f8cff;margin:6px 0 2px 0;'>📁 Projet courant : <b>{chemin}</b></div>")
            self.afficher_arborescence_fichiers(chemin)

    def afficher_arborescence_fichiers(self, chemin):
        self.files_tree.clear()
        def ajouter_noeud(parent, path):
            try:
                entries = sorted(os.listdir(path))
            except Exception:
                return
            for entry in entries:
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    node = QTreeWidgetItem(["📁 " + entry])
                    parent.addChild(node)
                    ajouter_noeud(node, full_path)
                else:
                    node = QTreeWidgetItem(["📄 " + entry])
                    parent.addChild(node)
        if os.path.isdir(chemin):
            root = QTreeWidgetItem(["📁 " + os.path.basename(chemin)])
            self.files_tree.addTopLevelItem(root)
            ajouter_noeud(root, chemin)
            self.files_tree.expandItem(root)

    def envoyer_message(self):
        texte = self.input.text().strip()
        if texte:
            # Affichage bulle utilisateur (dark)
            self.history.append(f"<div style='background:#2a2f3b;padding:8px 12px;border-radius:10px;max-width:80%;margin:8px 0 8px auto;text-align:right;color:#dbeafe;'><b>Vous :</b> {texte}</div>")
            self.input.clear()
            # Affichage réflexion IA (petit, italique, fond sombre doux)
            self.history.append("""
                <div style='background:#232837;color:#8fa0c7;font-size:13px;font-style:italic;padding:7px 12px;border-radius:8px;max-width:72%;margin:4px auto 4px 0;text-align:left;'>
                ⏳ <i>L'IA réfléchit...</i>
                </div>
            """)
            QApplication.processEvents()
            # Appel agent IA avec contexte projet courant ET tous les projets ouverts
            reponse = self.agent.traiter_instruction(
                texte,
                projet_courant=self.projet_courant,
                projets_ouverts=self.projets if self.projets else ([self.projet_courant] if self.projet_courant else None)
            )
            # Affichage bulle IA (dark, claire, markdown-friendly)
            import re
            code_blocks = re.findall(r'```(.*?)```', reponse, re.DOTALL)
            self._last_code_blocks = code_blocks  # Stocker les extraits de code pour accès par index
            self.history.append(f"<div style='background:#22242a;padding:13px 16px;border-radius:12px;max-width:82%;margin:10px auto 10px 0;text-align:left;color:#ffeac2;font-size:15px;line-height:1.6;'><b>IA :</b><br>{self._format_ia_response(reponse)}</div>")
            self.history.anchorClicked.connect(self._handle_anchor_click)  # Connecter anchorClicked à un slot
            self.history.moveCursor(self.history.textCursor().End)

    def _format_ia_response(self, texte):
        """
        Améliore l'affichage des réponses IA :
        - Bloc réflexion IA stylé si <details><summary>...> trouvé
        - Titres, sous-titres, listes markdown
        - Blocs code/terminal améliorés
        - Rendu moderne et lisible
        """
        import html, re
        t = texte
        # 1. Supprimer complètement la réflexion IA (<details><summary>...>...</details>)
        t = re.sub(r'<details><summary>.*?</summary>.*?</details>', '', t, flags=re.DOTALL)
        # 2. Code blocks (```lang\n...```)
        code_blocks = re.findall(r'```([a-zA-Z0-9]*)\n(.*?)```', t, re.DOTALL)
        for idx, (lang, code) in enumerate(code_blocks):
            is_command = lang.lower() in ('bash','sh','zsh','shell') or code.strip().startswith('$') or code.strip().startswith('!')
            code_html = (
                f'<div style="position:relative;background:#181c24;border-radius:10px;box-shadow:0 2px 8px #0004;padding:10px 12px 12px 12px;margin:14px 0 10px 0;transition:box-shadow 0.2s;">'
                f'<pre style="margin:0;font-size:14px;color:#b2e1ff;">{html.escape(code)}</pre>'
                f'<a href="copy:{idx}" style="position:absolute;top:8px;right:54px;font-size:11px;padding:2px 8px;border-radius:6px;background:#4f8cff;color:white;text-decoration:none;opacity:0.85;">Copy</a>'
            )
            if is_command:
                code_html += (
                    f'<a href="run:{idx}" style="position:absolute;top:8px;right:8px;font-size:11px;padding:2px 8px;border-radius:6px;background:#34c759;color:white;text-decoration:none;opacity:0.85;">Run</a>'
                )
            code_html += "</div>"
            t = t.replace(f'```{lang}\n{code}```', code_html)
        # 3. Titres markdown
        t = re.sub(r'^# (.*?)<br>', r'<div style="font-size:21px;font-weight:bold;color:#8fb3ff;margin:16px 0 8px 0;">\1</div>', t, flags=re.MULTILINE)
        t = re.sub(r'^## (.*?)<br>', r'<div style="font-size:18px;font-weight:bold;color:#6bc1ff;margin:12px 0 6px 0;">\1</div>', t, flags=re.MULTILINE)
        t = re.sub(r'^### (.*?)<br>', r'<div style="font-size:16px;font-weight:bold;color:#4f8cff;margin:8px 0 4px 0;">\1</div>', t, flags=re.MULTILINE)
        # 4. Listes markdown
        t = re.sub(r'(<br>|^)\s*[-*] (.*?)<br>', r'\1<div style="margin-left:22px;">• \2</div>', t)
        t = re.sub(r'(<br>|^)\s*\d+\. (.*?)<br>', r'\1<div style="margin-left:22px;">◦ \2</div>', t)
        # 5. Gras, italique
        t = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', t)
        t = re.sub(r'__(.*?)__', r'<b>\1</b>', t)
        t = re.sub(r'\*(.*?)\*', r'<i>\1</i>', t)
        # 6. Sauts de ligne, indentation
        t = t.replace('\n', '<br>')
        t = t.replace('    ', '&nbsp;&nbsp;&nbsp;&nbsp;')
        # 7. Nettoyage
        t = t.replace('<br><br>', '<br>')
        # 8. Rendu final : uniquement la réponse sans réflexion
        return t.strip()

    def _handle_anchor_click(self, url):
        # Slot pour gérer les clics sur les liens copy:/run:
        scheme = url.scheme()
        path = url.path().lstrip('/')
        try:
            idx = int(path)
        except Exception:
            return
        if hasattr(self, '_last_code_blocks') and idx < len(self._last_code_blocks):
            if scheme == 'copy':
                self.copy_code_to_clipboard(self._last_code_blocks[idx])
            elif scheme == 'run':
                self.execute_command(self._last_code_blocks[idx])
