import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QTextEdit, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QWidget, 
                             QFileDialog, QMessageBox, QMenu, QAction)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QSettings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notepad")
        self.setGeometry(700, 300, 500, 500)
        self.settings = QSettings("MyCompany", "MyNotepad")
        self.recent_files = []
        
        self.init_main_ui()
        self.load_recent_files()
        
    def init_main_ui(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Welcome label
        label = QLabel("Welcome User")
        label.setFont(QFont("Arial", 40))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Notes button
        self.notes_button = QPushButton("Notes")
        self.notes_button.setStyleSheet("font-size: 25px; font-family: Arial;")
        self.notes_button.clicked.connect(self.open_notes)
        buttons_layout.addWidget(self.notes_button)
        
        # To-do button
        self.todo_button = QPushButton("To-do")
        self.todo_button.setStyleSheet("font-size: 25px; font-family: Arial;")
        self.todo_button.clicked.connect(self.open_todo)
        buttons_layout.addWidget(self.todo_button)
        
        layout.addLayout(buttons_layout)
        
        # Create menu bar
        self.create_menu_bar()
        
    def create_menu_bar(self):
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("File")
        
        # Recent files submenu
        self.recent_menu = file_menu.addMenu("Open Recent")
        self.update_recent_menu()
        
        # Clear history action
        clear_action = QAction("Clear History", self)
        clear_action.triggered.connect(self.clear_recent_files)
        file_menu.addAction(clear_action)
        
    def update_recent_menu(self):
        self.recent_menu.clear()
        for file_path in self.recent_files:
            action = QAction(file_path, self)
            action.triggered.connect(lambda checked, path=file_path: self.open_recent_file(path))
            self.recent_menu.addAction(action)
        
    def open_recent_file(self, file_path):
        if os.path.exists(file_path):
            editor = TextEditorWindow("Notes" if file_path.endswith('.txt') else "To-do")
            editor.current_file = file_path
            editor.setWindowTitle(f"{editor.editor_type} - {os.path.basename(file_path)}")
            with open(file_path, 'r') as file:
                editor.text_edit.setPlainText(file.read())
            editor.show()
            self.hide()
        else:
            QMessageBox.warning(self, "Error", f"The file {file_path} no longer exists.")
            self.recent_files.remove(file_path)
            self.save_recent_files()
            self.update_recent_menu()
        
    def add_recent_file(self, file_path):
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > 5:  # Keep only last 5 files
            self.recent_files = self.recent_files[:5]
        self.save_recent_files()
        self.update_recent_menu()
        
    def save_recent_files(self):
        self.settings.setValue("recent_files", self.recent_files)
        
    def load_recent_files(self):
        self.recent_files = self.settings.value("recent_files", [])
        
    def clear_recent_files(self):
        self.recent_files = []
        self.save_recent_files()
        self.update_recent_menu()
        
    def open_notes(self):
        self.text_editor = TextEditorWindow("Notes", self)
        self.text_editor.show()
        self.hide()
        
    def open_todo(self):
        self.text_editor = TextEditorWindow("To-do", self)
        self.text_editor.show()
        self.hide()

class TextEditorWindow(QMainWindow):
    def __init__(self, editor_type, main_window=None):
        super().__init__()
        self.editor_type = editor_type
        self.current_file = None
        self.main_window = main_window
        self.setWindowTitle(f"{editor_type} - Untitled")
        self.setGeometry(700, 300, 800, 600)
        
        self.init_editor_ui()
        
    def init_editor_ui(self):
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Text edit area
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Back button
        back_button = QPushButton("Back to Main")
        back_button.setStyleSheet("font-size: 16px; font-family: Arial;")
        back_button.clicked.connect(self.back_to_main)
        button_layout.addWidget(back_button)
        
        # Open button
        open_button = QPushButton("Open File")
        open_button.setStyleSheet("font-size: 16px; font-family: Arial;")
        open_button.clicked.connect(self.open_file)
        button_layout.addWidget(open_button)
        
        # Save button
        save_button = QPushButton("Save")
        save_button.setStyleSheet("font-size: 16px; font-family: Arial;")
        save_button.clicked.connect(self.save_file)
        button_layout.addWidget(save_button)
        
        # Delete button
        delete_button = QPushButton("Delete File")
        delete_button.setStyleSheet("font-size: 16px; font-family: Arial;")
        delete_button.clicked.connect(self.delete_file)
        button_layout.addWidget(delete_button)
        
        layout.addLayout(button_layout)
        
    def back_to_main(self):
        if self.main_window:
            self.main_window.show()
        self.close()
        
    def open_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", 
                                                 "Text Files (*.txt);;All Files (*)", 
                                                 options=options)
        if file_name:
            self.current_file = file_name
            self.setWindowTitle(f"{self.editor_type} - {os.path.basename(file_name)}")
            with open(file_name, 'r') as file:
                self.text_edit.setPlainText(file.read())
            if self.main_window:
                self.main_window.add_recent_file(file_name)
                
    def save_file(self):
        if self.current_file:
            with open(self.current_file, 'w') as file:
                file.write(self.text_edit.toPlainText())
            if self.main_window:
                self.main_window.add_recent_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File", "", 
                                                 "Text Files (*.txt);;All Files (*)", 
                                                 options=options)
        if file_name:
            self.current_file = file_name
            self.setWindowTitle(f"{self.editor_type} - {os.path.basename(file_name)}")
            with open(file_name, 'w') as file:
                file.write(self.text_edit.toPlainText())
            if self.main_window:
                self.main_window.add_recent_file(file_name)
    
    def delete_file(self):
        if not self.current_file:
            QMessageBox.warning(self, "Error", "No file is currently open to delete.")
            return
            
        reply = QMessageBox.question(self, 'Delete File', 
                                    f"Are you sure you want to delete {os.path.basename(self.current_file)}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                os.remove(self.current_file)
                QMessageBox.information(self, "Success", "File deleted successfully.")
                self.current_file = None
                self.text_edit.clear()
                self.setWindowTitle(f"{self.editor_type} - Untitled")
                if self.main_window:
                    self.main_window.recent_files.remove(self.current_file)
                    self.main_window.save_recent_files()
                    self.main_window.update_recent_menu()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete file: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())