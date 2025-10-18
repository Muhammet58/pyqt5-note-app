from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QSizePolicy, 
    QListWidget, QTextEdit, QPushButton, QLabel, QListWidgetItem, QFrame, QMessageBox)
from PyQt5.QtWidgets import QStackedLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from datetime import datetime
import sys, json, csv, os

class NoteBook(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notebook")
        self.setWindowIcon(QIcon("files/cartoon-notebook-pen-icon.png"))
        self.resize(1000, 600)
        self.is_dark_theme = True
        self.data_dir = os.path.join(os.getcwd(), "data")
        self.json_path = os.path.join(self.data_dir, "notes.json")
        self.csv_path = os.path.join(self.data_dir, "notes.csv")
        
        self.build_ui()
        self.apply_theme()
        self.ensure_data_files()
        self.load_notes()
        self.update_empty_state()

    def build_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        left_panel = QVBoxLayout()

        left_top_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        left_top_layout.addWidget(self.search_bar)

        self.note_count = QLabel()
        left_top_layout.addWidget(self.note_count)

        left_panel.addLayout(left_top_layout)

        self.note_list = QListWidget()
        self.note_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.empty_label = QLabel("Henüz not eklenmemiş.")
        self.empty_label.setAlignment(Qt.AlignCenter)

        self.note_stack = QStackedLayout()
        self.note_stack.addWidget(self.empty_label)
        self.note_stack.addWidget(self.note_list)

        left_panel.addLayout(self.note_stack)

        self.new_note_btn = QPushButton("+ New Note")
        left_panel.addWidget(self.new_note_btn)

        right_panel = QVBoxLayout()

        top_row = QHBoxLayout()
        self.note_title = QLineEdit()
        self.note_title.setFixedWidth(500)
        
        top_row.addWidget(self.note_title)
        top_row.addStretch()

        self.theme_btn = QPushButton("Light Theme")
        top_row.addWidget(self.theme_btn)
        right_panel.addLayout(top_row)

        self.text_edit = QTextEdit()

        right_panel.addWidget(self.text_edit)

        bottom_row = QHBoxLayout()
        self.updated_label = QLabel()
        bottom_row.addWidget(self.updated_label)
        bottom_row.addStretch()

        self.save_btn = QPushButton("Save")
        bottom_row.addWidget(self.save_btn)
        self.delete_btn = QPushButton("Delete")
        bottom_row.addWidget(self.delete_btn)
        self.export_btn = QPushButton("Export")
        bottom_row.addWidget(self.export_btn)

        right_panel.addLayout(bottom_row)

        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.VLine)
        main_layout.addLayout(left_panel, 3)
        main_layout.addWidget(self.divider)
        main_layout.addLayout(right_panel, 6)

        self.save_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

        self.note_list.itemSelectionChanged.connect(self.is_item_select)
        self.note_title.textChanged.connect(self.change_event_func)
        self.note_list.itemClicked.connect(self.display_note)
        self.save_btn.clicked.connect(self.save_note)
        self.delete_btn.clicked.connect(self.delete_note)
        self.new_note_btn.clicked.connect(self.new_note)
        self.export_btn.clicked.connect(self.export_csv)
        self.note_list.itemChanged.connect(self.update_empty_state)
        self.note_list.itemSelectionChanged.connect(self.update_empty_state)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.search_bar.textChanged.connect(self.search_function)

    def update_empty_state(self):
        if self.note_list.count() == 0:
            self.note_stack.setCurrentWidget(self.empty_label)
        else:
            self.note_stack.setCurrentWidget(self.note_list)

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self.apply_theme()

    def apply_theme(self):
        if getattr(self, "is_dark_theme", True):
            bg_main = "#121212"
            bg_widget = "#1e1e1e"
            bg_textedit = "#1b1b1b"
            text_color = "#eee"
            sub_text = "#777"
            divider_bg_color = "white"
            divider_color = "black"
            btn_bg = "#222"
            btn_hover = "#333"
            placeholder_color = "#888"
            self.theme_btn.setText("Light Theme")
        else:
            bg_main = "#f5f5f5"
            bg_widget = "#ffffff"
            bg_textedit = "#fafafa"
            text_color = "#111"
            sub_text = "#555"
            divider_bg_color = "black"
            divider_color = "white"
            btn_bg = "#e0e0e0"
            btn_hover = "#d0d0d0"
            placeholder_color = "#888"
            self.theme_btn.setText("Dark Theme")

        self.setStyleSheet(f"QMainWindow {{ background-color: {bg_main}; }}")

        self.search_bar.setStyleSheet(f"""
            QLineEdit {{
                background-color: {bg_widget};
                border: none;
                border-radius: 8px;
                padding: 8px;
                color: {text_color};
            }}
            QLineEdit::placeholder {{
                color: {placeholder_color};
            }}
        """)

        self.note_count.setStyleSheet(f"color: {text_color};")

        self.note_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {bg_textedit};
                border: none;
                color: {text_color};
            }}
            QListWidget::item:selected {{
                background-color: {btn_hover};
            }}
        """)

        self.empty_label.setStyleSheet(f"color: {sub_text}; font-style: italic;")

        self.note_title.setStyleSheet(f"""
            QLineEdit {{
                font-size: 15px;
                font-weight: bold;
                color: {text_color};
                background-color: {bg_textedit};
                border-radius: 10px;
                padding: 6px;
                border: none;
            }}
            QLineEdit::placeholder {{
                color: {placeholder_color};
            }}
        """)

        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {bg_textedit};
                color: {text_color};
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }}
        """)

        for btn in [self.save_btn, self.delete_btn, self.export_btn, self.theme_btn, self.new_note_btn]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {btn_bg};
                    color: {text_color};
                    border-radius: 8px;
                    padding: 10px;
                }}
                QPushButton:hover {{
                    background-color: {btn_hover};
                }}
            """)

        self.updated_label.setStyleSheet(f"color: {sub_text}; font-size: 12px;")

        self.divider.setStyleSheet(f"background-color: {divider_bg_color}; color: {divider_color}")


    def save_notes_to_file(self, notes):
        with open(self.json_path, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=4)

    def ensure_data_files(self):
        os.makedirs(self.data_dir, exist_ok=True)
        if not os.path.exists(self.json_path):
            self.save_notes_to_file([])
        if not os.path.exists(self.csv_path):
            open(self.csv_path, "w", encoding="utf-8").close()

    def load_notes_from_file(self):
        with open(self.json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def refresh_note_list(self, notes, selected_title=None):
        self.note_list.clear()
        for note in notes:
            item = QListWidgetItem(f"{note['title']}\ncreated: {note['created_at']}\n")
            self.note_list.addItem(item)
            if selected_title and note['title'] == selected_title:
                item.setSelected(True)
                self.note_list.setCurrentItem(item)
        self.note_count.setText(f"{self.note_list.count()} Note")

    def show_message_box(self, icon, text, title="Bilgilendirme", ok_text="Tamam", cancel=False):
        msg = QMessageBox()
        msg.setIcon(icon)
        msg.setText(text)
        msg.setWindowTitle(title)

        msg.adjustSize()
        parent_center = self.geometry().center()
        msg_geometry = msg.frameGeometry()
        msg_geometry.moveCenter(parent_center)
        msg.move(msg_geometry.topLeft())

        ok_btn = msg.addButton(ok_text, QMessageBox.AcceptRole)
        if cancel:
            msg.addButton("İptal", QMessageBox.RejectRole)
        msg.exec_()
        return msg.clickedButton() == ok_btn


    def is_item_select(self):
        selected_item = self.note_list.selectedItems()
        is_active = True if selected_item else False
        self.delete_btn.setEnabled(is_active)
        is_notes_list_empty = False if self.note_list.count() == 0 else True
        self.export_btn.setEnabled(is_notes_list_empty)

    def change_event_func(self, text):
        is_active = True if text else False
        self.save_btn.setEnabled(is_active)

    def load_notes(self):
        notes = self.load_notes_from_file()
        self.refresh_note_list(notes)
        if not notes:
            self.export_btn.setEnabled(False)

    def display_note(self, item):
        title = item.text().split("\n")[0]
        notes = self.load_notes_from_file()
        selected_note = next((n for n in notes if n["title"] == title), None)
        if selected_note:
            self.note_title.setText(selected_note["title"])
            self.text_edit.setText(selected_note["content"])
            self.updated_label.setText(f"Updated: {selected_note['updated_at']}")

    def new_note(self):
        selected_item = self.note_list.currentItem()
        if selected_item:
            title = selected_item.text().split('\n')[0]
            current_title = self.note_title.text()
            current_content = self.text_edit.toPlainText()
            notes = self.load_notes_from_file()

            for note in notes:
                if note['title'] == title:
                    if current_title != note['title'] or current_content != note['content']:
                        msg_box = self.show_message_box(QMessageBox.Warning, 
                            "Kaydedilmemiş değişiklikler var. Kaydetmeden devam etmek istiyor musunuz?", "Uyarı", "Evet", cancel=True)
                        if not msg_box:
                            return
                    break

        self.note_title.clear()
        self.text_edit.clear()
        self.note_list.clearSelection()

    def save_note(self):
        selected_item = self.note_list.selectedItems()
        selected_item_title = selected_item[0].text().split("\n")[0] if selected_item else None
        title = self.note_title.text().strip()
        content = self.text_edit.toPlainText()
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        notes = self.load_notes_from_file()
        selected_existing_note = next((n for n in notes if n["title"] == selected_item_title), None)
        existing_note = next((n for n in notes if n["title"] == title), None)

        if existing_note and not selected_item:
            self.show_message_box(QMessageBox.Warning, "Aynı başlıkla başka bir not zaten mevcut!", "Uyarı")
            return

        if selected_existing_note:
            selected_existing_note_index = notes.index(selected_existing_note)
            selected_note = notes[selected_existing_note_index]
            selected_note["title"] = title
            selected_note["content"] = content
            selected_note["updated_at"] = now
            self.updated_label.setText(f"Updated: {now}")
            self.refresh_note_list(notes, selected_title=title)
            self.show_message_box(QMessageBox.Information, f"{title} başlıklı not güncellendi.")
        else:
            new_note = {"title": title, "content": content, "created_at": now, "updated_at": now}
            notes.append(new_note)
            self.refresh_note_list(notes, selected_title=title)
            self.show_message_box(QMessageBox.Information, "Not eklendi.", "Bilgilendirme")

        self.save_notes_to_file(notes)

    def delete_note(self):
        selected = self.note_list.currentItem()
        if not selected:
            return
        
        title = selected.text().split("\n")[0]
        if not self.show_message_box(QMessageBox.Warning, f"{title} başlıklı not silinsin mi?", "Sil", "Evet", cancel=True):
            return
        
        notes = self.load_notes_from_file()
        notes = [n for n in notes if n["title"] != title]
        self.save_notes_to_file(notes)
        self.refresh_note_list(notes)
        self.note_title.clear()
        self.text_edit.clear()
        self.updated_label.clear()
        if not notes:
            self.export_btn.setEnabled(False)
            self.update_empty_state()

    def export_csv(self):
        notes = self.load_notes_from_file()
        with open(self.csv_path, 'w', encoding='utf-8', newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['title', 'content', 'created_at', 'updated_at'])
            writer.writeheader()
            writer.writerows(notes)
        self.show_message_box(QMessageBox.Information, "Notlar CSV olarak dışa aktarıldı.", "Bilgilendirme")

    def search_function(self):
        search_text = self.search_bar.text().strip().lower()
        notes = self.load_notes_from_file()
        selected_item = self.note_list.currentItem()
        selected_title = selected_item.text().split("\n")[0] if selected_item else None

        filtered = [n for n in notes if search_text in n["title"].lower()] if search_text else notes
        self.refresh_note_list(filtered, selected_title)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NoteBook()
    window.show()
    sys.exit(app.exec_())