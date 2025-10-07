"""
Teacher Interface for Creating and Managing Teaching Modules
This interface allows teachers to create custom learning activities for children.
"""

import sys
import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Any
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox, QFileDialog,
    QListWidget, QListWidgetItem, QGroupBox, QFormLayout, QMessageBox,
    QTabWidget, QScrollArea, QGridLayout, QSpinBox, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QIcon

class TeachingModule:
    """Represents a single teaching module created by a teacher"""
    
    def __init__(self):
        self.id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.title = ""
        self.description = ""
        self.subject = "general"
        self.difficulty_level = 1  # 1-5
        self.content_type = "text"  # text, voice, game
        self.input_method = "voice"  # voice, fingers, placard
        self.game_type = "quiz"  # quiz, matching, classification
        self.questions = []
        self.resources = []  # List of uploaded files
        self.created_date = datetime.now()
        self.tags = []
    
    def to_dict(self):
        """Convert module to dictionary for JSON storage"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'subject': self.subject,
            'difficulty_level': self.difficulty_level,
            'content_type': self.content_type,
            'input_method': self.input_method,
            'game_type': self.game_type,
            'questions': self.questions,
            'resources': self.resources,
            'created_date': self.created_date.isoformat(),
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create module from dictionary"""
        module = cls()
        module.id = data.get('id', module.id)
        module.title = data.get('title', '')
        module.description = data.get('description', '')
        module.subject = data.get('subject', 'general')
        module.difficulty_level = data.get('difficulty_level', 1)
        module.content_type = data.get('content_type', 'text')
        module.input_method = data.get('input_method', 'voice')
        module.game_type = data.get('game_type', 'quiz')
        module.questions = data.get('questions', [])
        module.resources = data.get('resources', [])
        module.created_date = datetime.fromisoformat(data.get('created_date', datetime.now().isoformat()))
        module.tags = data.get('tags', [])
        return module

class ModuleCreatorWidget(QWidget):
    """Widget for creating new teaching modules"""
    
    module_created = pyqtSignal(TeachingModule)
    
    def __init__(self):
        super().__init__()
        self.current_module = TeachingModule()
        self.uploaded_files = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Basic Information Group
        basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout()
        
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("e.g., Fruits vs Vegetables Classification")
        basic_layout.addRow("Module Title:", self.title_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Brief description of what children will learn...")
        basic_layout.addRow("Description:", self.description_edit)
        
        self.subject_combo = QComboBox()
        self.subject_combo.addItems(["Math", "Science", "Health", "Reading", "General"])
        basic_layout.addRow("Subject:", self.subject_combo)
        
        self.difficulty_spin = QSpinBox()
        self.difficulty_spin.setRange(1, 5)
        self.difficulty_spin.setValue(1)
        basic_layout.addRow("Difficulty (1-5):", self.difficulty_spin)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Interaction Settings Group
        interaction_group = QGroupBox("How should the bot interact with children?")
        interaction_layout = QFormLayout()
        
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems(["Voice + Text", "Voice Only", "Text Only", "Interactive Game"])
        interaction_layout.addRow("Bot Display Method:", self.content_type_combo)
        
        self.input_method_combo = QComboBox()
        self.input_method_combo.addItems(["Voice Response", "Finger Counting", "Placard (Yes/No)", "Multiple Choice"])
        interaction_layout.addRow("Child Input Method:", self.input_method_combo)
        
        self.game_type_combo = QComboBox()
        self.game_type_combo.addItems(["Classification (Right/Wrong)", "Counting Game", "Memory Game", "Quiz Game"])
        interaction_layout.addRow("Game Type:", self.game_type_combo)
        
        interaction_group.setLayout(interaction_layout)
        layout.addWidget(interaction_group)
        
        # Content Creation Group
        content_group = QGroupBox("Create Learning Content")
        content_layout = QVBoxLayout()
        
        # Question/Activity Creator
        question_layout = QHBoxLayout()
        self.question_edit = QLineEdit()
        self.question_edit.setPlaceholderText("Enter a question or activity prompt...")
        question_layout.addWidget(QLabel("Question/Prompt:"))
        question_layout.addWidget(self.question_edit)
        
        add_question_btn = QPushButton("Add Question")
        add_question_btn.clicked.connect(self.add_question)
        question_layout.addWidget(add_question_btn)
        
        content_layout.addLayout(question_layout)
        
        # Questions List
        self.questions_list = QListWidget()
        content_layout.addWidget(QLabel("Questions/Activities:"))
        content_layout.addWidget(self.questions_list)
        
        content_group.setLayout(content_layout)
        layout.addWidget(content_group)
        
        # Resource Upload Group
        resource_group = QGroupBox("Upload Learning Resources")
        resource_layout = QVBoxLayout()
        
        upload_layout = QHBoxLayout()
        upload_btn = QPushButton("Upload Images/Files")
        upload_btn.clicked.connect(self.upload_resources)
        upload_layout.addWidget(upload_btn)
        
        self.resource_list = QListWidget()
        resource_layout.addLayout(upload_layout)
        resource_layout.addWidget(QLabel("Uploaded Resources:"))
        resource_layout.addWidget(self.resource_list)
        
        resource_group.setLayout(resource_layout)
        layout.addWidget(resource_group)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        preview_btn = QPushButton("Preview Module")
        preview_btn.clicked.connect(self.preview_module)
        button_layout.addWidget(preview_btn)
        
        save_btn = QPushButton("Save Module")
        save_btn.clicked.connect(self.save_module)
        save_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        button_layout.addWidget(save_btn)
        
        clear_btn = QPushButton("Clear All")
        clear_btn.clicked.connect(self.clear_form)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_question(self):
        """Add a question to the current module"""
        question_text = self.question_edit.text().strip()
        if question_text:
            self.current_module.questions.append({
                'question': question_text,
                'type': self.game_type_combo.currentText(),
                'answer': '',  # Will be filled based on game type
                'resources': []  # Associated images/files
            })
            
            self.questions_list.addItem(f"Q{len(self.current_module.questions)}: {question_text}")
            self.question_edit.clear()
    
    def upload_resources(self):
        """Upload images and other resources"""
        file_dialog = QFileDialog()
        files, _ = file_dialog.getOpenFileNames(
            self, 
            "Select Learning Resources", 
            "", 
            "Images (*.png *.jpg *.jpeg *.gif);;All Files (*)"
        )
        
        if files:
            for file_path in files:
                filename = os.path.basename(file_path)
                # Copy file to resources directory
                resources_dir = "teaching_modules/resources"
                os.makedirs(resources_dir, exist_ok=True)
                
                dest_path = os.path.join(resources_dir, f"{self.current_module.id}_{filename}")
                shutil.copy2(file_path, dest_path)
                
                self.current_module.resources.append(dest_path)
                self.resource_list.addItem(filename)
    
    def preview_module(self):
        """Preview the created module"""
        self.update_module_from_form()
        
        preview_text = f"""
Module Preview:
Title: {self.current_module.title}
Subject: {self.current_module.subject}
Difficulty: {self.current_module.difficulty_level}/5
Content Type: {self.current_module.content_type}
Input Method: {self.current_module.input_method}
Game Type: {self.current_module.game_type}

Questions: {len(self.current_module.questions)}
Resources: {len(self.current_module.resources)}

Description:
{self.current_module.description}
        """
        
        QMessageBox.information(self, "Module Preview", preview_text)
    
    def save_module(self):
        """Save the current module"""
        self.update_module_from_form()
        
        if not self.current_module.title:
            QMessageBox.warning(self, "Error", "Please enter a module title.")
            return
        
        if not self.current_module.questions:
            QMessageBox.warning(self, "Error", "Please add at least one question or activity.")
            return
        
        # Save module to file
        modules_dir = "teaching_modules"
        os.makedirs(modules_dir, exist_ok=True)
        
        module_file = os.path.join(modules_dir, f"{self.current_module.id}.json")
        with open(module_file, 'w') as f:
            json.dump(self.current_module.to_dict(), f, indent=2)
        
        QMessageBox.information(self, "Success", f"Module '{self.current_module.title}' saved successfully!")
        
        self.module_created.emit(self.current_module)
        self.clear_form()
    
    def update_module_from_form(self):
        """Update the current module with form data"""
        self.current_module.title = self.title_edit.text()
        self.current_module.description = self.description_edit.toPlainText()
        self.current_module.subject = self.subject_combo.currentText().lower()
        self.current_module.difficulty_level = self.difficulty_spin.value()
        self.current_module.content_type = self.content_type_combo.currentText()
        self.current_module.input_method = self.input_method_combo.currentText()
        self.current_module.game_type = self.game_type_combo.currentText()
    
    def clear_form(self):
        """Clear all form fields"""
        self.current_module = TeachingModule()
        self.title_edit.clear()
        self.description_edit.clear()
        self.subject_combo.setCurrentIndex(0)
        self.difficulty_spin.setValue(1)
        self.content_type_combo.setCurrentIndex(0)
        self.input_method_combo.setCurrentIndex(0)
        self.game_type_combo.setCurrentIndex(0)
        self.question_edit.clear()
        self.questions_list.clear()
        self.resource_list.clear()

class ModuleManagerWidget(QWidget):
    """Widget for managing existing teaching modules"""
    
    def __init__(self):
        super().__init__()
        self.modules = []
        self.init_ui()
        self.load_modules()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Saved Teaching Modules"))
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_modules)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Modules List
        self.modules_list = QListWidget()
        self.modules_list.itemDoubleClicked.connect(self.view_module)
        layout.addWidget(self.modules_list)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        view_btn = QPushButton("View Details")
        view_btn.clicked.connect(self.view_selected_module)
        button_layout.addWidget(view_btn)
        
        deploy_btn = QPushButton("Deploy to Bot")
        deploy_btn.clicked.connect(self.deploy_module)
        deploy_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; }")
        button_layout.addWidget(deploy_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_module)
        delete_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        button_layout.addWidget(delete_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def load_modules(self):
        """Load all saved teaching modules"""
        self.modules.clear()
        self.modules_list.clear()
        
        modules_dir = "teaching_modules"
        if not os.path.exists(modules_dir):
            return
        
        for filename in os.listdir(modules_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(modules_dir, filename), 'r') as f:
                        module_data = json.load(f)
                        module = TeachingModule.from_dict(module_data)
                        self.modules.append(module)
                        
                        item_text = f"{module.title} ({module.subject.title()}) - Level {module.difficulty_level}"
                        self.modules_list.addItem(item_text)
                except Exception as e:
                    print(f"Error loading module {filename}: {e}")
    
    def view_selected_module(self):
        """View details of the selected module"""
        current_row = self.modules_list.currentRow()
        if current_row >= 0:
            self.view_module(self.modules_list.item(current_row))
    
    def view_module(self, item):
        """View details of a module"""
        row = self.modules_list.row(item)
        if row >= 0 and row < len(self.modules):
            module = self.modules[row]
            
            details = f"""
Module: {module.title}
Subject: {module.subject.title()}
Difficulty: {module.difficulty_level}/5
Created: {module.created_date.strftime('%Y-%m-%d %H:%M')}

Description:
{module.description}

Content Type: {module.content_type}
Input Method: {module.input_method}
Game Type: {module.game_type}

Questions ({len(module.questions)}):
"""
            for i, q in enumerate(module.questions, 1):
                details += f"{i}. {q['question']}\n"
            
            details += f"\nResources: {len(module.resources)} file(s)"
            
            QMessageBox.information(self, f"Module: {module.title}", details)
    
    def deploy_module(self):
        """Deploy module to the teaching bot"""
        current_row = self.modules_list.currentRow()
        if current_row >= 0:
            module = self.modules[current_row]
            
            # Copy module to active deployment directory
            deploy_dir = "active_modules"
            os.makedirs(deploy_dir, exist_ok=True)
            
            deploy_file = os.path.join(deploy_dir, f"{module.id}.json")
            with open(deploy_file, 'w') as f:
                json.dump(module.to_dict(), f, indent=2)
            
            QMessageBox.information(
                self, 
                "Deployed", 
                f"Module '{module.title}' has been deployed to the teaching bot!\n\nChildren can now access this learning activity."
            )
    
    def delete_module(self):
        """Delete the selected module"""
        current_row = self.modules_list.currentRow()
        if current_row >= 0:
            module = self.modules[current_row]
            
            reply = QMessageBox.question(
                self, 
                "Confirm Delete", 
                f"Are you sure you want to delete '{module.title}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Delete module file
                module_file = f"teaching_modules/{module.id}.json"
                if os.path.exists(module_file):
                    os.remove(module_file)
                
                # Delete associated resources
                for resource in module.resources:
                    if os.path.exists(resource):
                        os.remove(resource)
                
                QMessageBox.information(self, "Deleted", f"Module '{module.title}' has been deleted.")
                self.load_modules()

class TeacherInterface(QMainWindow):
    """Main teacher interface application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Teaching Module Creator - Humanoid Assistant")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Teaching Module Creator")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("QLabel { color: #2196F3; margin: 10px; }")
        layout.addWidget(title)
        
        subtitle = QLabel("Create custom learning activities for your humanoid teaching assistant")
        subtitle.setFont(QFont("Arial", 12))
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("QLabel { color: #666; margin-bottom: 20px; }")
        layout.addWidget(subtitle)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        
        # Module Creator Tab
        self.creator_widget = ModuleCreatorWidget()
        self.tab_widget.addTab(self.creator_widget, "Create New Module")
        
        # Module Manager Tab
        self.manager_widget = ModuleManagerWidget()
        self.tab_widget.addTab(self.manager_widget, "Manage Modules")
        
        layout.addWidget(self.tab_widget)
        
        central_widget.setLayout(layout)
        
        # Connect signals
        self.creator_widget.module_created.connect(self.on_module_created)
        
        # Create menus
        self.create_menus()
    
    def create_menus(self):
        """Create application menus"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        file_menu.addAction('New Module', self.new_module)
        file_menu.addSeparator()
        file_menu.addAction('Import Module', self.import_module)
        file_menu.addAction('Export Module', self.export_module)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About', self.show_about)
        help_menu.addAction('User Guide', self.show_guide)
    
    def new_module(self):
        """Create a new module"""
        self.tab_widget.setCurrentIndex(0)
        self.creator_widget.clear_form()
    
    def import_module(self):
        """Import a module from file"""
        file_path, _ = QFileDialog.getOpenFileName(self, "Import Module", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    module_data = json.load(f)
                    module = TeachingModule.from_dict(module_data)
                    
                    # Save to modules directory
                    modules_dir = "teaching_modules"
                    os.makedirs(modules_dir, exist_ok=True)
                    
                    new_file = os.path.join(modules_dir, f"{module.id}.json")
                    with open(new_file, 'w') as f:
                        json.dump(module.to_dict(), f, indent=2)
                    
                    QMessageBox.information(self, "Success", "Module imported successfully!")
                    self.manager_widget.load_modules()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import module: {e}")
    
    def export_module(self):
        """Export a module to file"""
        current_row = self.manager_widget.modules_list.currentRow()
        if current_row >= 0:
            module = self.manager_widget.modules[current_row]
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Module", 
                f"{module.title}.json",
                "JSON Files (*.json)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'w') as f:
                        json.dump(module.to_dict(), f, indent=2)
                    QMessageBox.information(self, "Success", "Module exported successfully!")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to export module: {e}")
        else:
            QMessageBox.warning(self, "Warning", "Please select a module to export.")
    
    def on_module_created(self, module):
        """Handle when a new module is created"""
        self.manager_widget.load_modules()
        self.tab_widget.setCurrentIndex(1)  # Switch to manager tab
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
Teaching Module Creator v1.0

Create custom learning activities for your humanoid teaching assistant.

Features:
• Create interactive learning modules
• Upload images and resources
• Choose interaction methods (voice, placard, fingers)
• Deploy modules to the teaching bot
• Manage existing modules

Developed for the Humanoid Teaching Assistant Capstone Project.
        """
        QMessageBox.about(self, "About", about_text)
    
    def show_guide(self):
        """Show user guide"""
        guide_text = """
Quick Start Guide:

1. CREATE A MODULE:
   • Enter title and description
   • Choose subject and difficulty
   • Select how the bot should interact
   • Add questions/activities
   • Upload images if needed

2. MANAGE MODULES:
   • View all created modules
   • Deploy modules to the bot
   • Delete unwanted modules

3. INTERACTION TYPES:
   • Voice + Text: Bot speaks and shows text
   • Placard: Child shows yes/no cards
   • Finger Counting: Child shows fingers
   • Voice Response: Child speaks answer

4. GAME TYPES:
   • Classification: Right/Wrong activities
   • Counting: Number recognition
   • Memory: Recall activities
   • Quiz: Question and answer

Example: "Fruits vs Vegetables"
• Title: Fruit or Vegetable Classification
• Upload fruit and vegetable images
• Game Type: Classification
• Input: Placard (Yes/No)
• Bot shows image, asks "Is this a fruit?"
• Child shows YES or NO placard
        """
        QMessageBox.information(self, "User Guide", guide_text)

def main():
    """Main function to run the teacher interface"""
    app = QApplication(sys.argv)
    app.setApplicationName("Teaching Module Creator")
    
    # Set application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 1ex;
            padding-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
        QPushButton {
            background-color: #e1e1e1;
            border: 1px solid #ccc;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #d4edda;
        }
        QPushButton:pressed {
            background-color: #c3e6cb;
        }
    """)
    
    window = TeacherInterface()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())