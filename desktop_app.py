#!/usr/bin/env python3
"""
AAMUSTED Counselling Management System - Desktop Application
Native desktop application without browser dependency
"""

import sys
import os
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTabWidget, QTableWidget, QTableWidgetItem,
                             QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox,
                             QDateEdit, QTimeEdit, QMessageBox, QGroupBox,
                             QSplitter, QMenuBar, QStatusBar, QDialog, QFormLayout,
                             QDialogButtonBox, QCheckBox, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt, QDate, QTime, QTimer
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from werkzeug.security import generate_password_hash, check_password_hash

class DatabaseManager:
    """Handle all database operations"""
    
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'counseling.db')
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialize database if it doesn't exist"""
        conn = self.get_connection()
        
        # Create tables (simplified from original)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS Student (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                programme TEXT,
                contact TEXT,
                index_number TEXT UNIQUE,
                department TEXT,
                faculty TEXT,
                parent_contact TEXT,
                hall_of_residence TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS Counsellor (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS Appointment (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                Counsellor_id INTEGER,
                date DATE NOT NULL,
                time TIME NOT NULL,
                purpose TEXT,
                status TEXT DEFAULT 'scheduled',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES Student (id),
                FOREIGN KEY (Counsellor_id) REFERENCES Counsellor (id)
            )''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS Session (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER,
                session_date DATETIME,
                notes TEXT,
                outcome TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (appointment_id) REFERENCES Appointment (id)
            )''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS Referral (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                referred_to TEXT,
                reason TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES Session (id)
            )''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_name TEXT PRIMARY KEY,
                setting_value TEXT
            )''')
        
        # Insert sample Counsellors if none exist
        conn.execute("INSERT OR IGNORE INTO Counsellor (id, name, contact) VALUES (1, 'Dr. Sarah Mensah', '0244-123-456')")
        conn.execute("INSERT OR IGNORE INTO Counsellor (id, name, contact) VALUES (2, 'Mr. Kwame Asante', '0244-987-654')")
        conn.execute("INSERT OR IGNORE INTO Counsellor (id, name, contact) VALUES (3, 'Ms. Abena Osei', '0244-555-789')")
        
        # Set a default password if not already set
        conn.execute("INSERT OR IGNORE INTO app_settings (setting_name, setting_value) VALUES (?, ?)",
                      ('password_hash', generate_password_hash('admin')))

        conn.commit()
        conn.close()

    def check_password(self, password):
        conn = self.get_connection()
        result = conn.execute("SELECT setting_value FROM app_settings WHERE setting_name = 'password_hash'").fetchone()
        conn.close()
        if result and check_password_hash(result['setting_value'], password):
            return True
        return False

    def set_password(self, new_password):
        conn = self.get_connection()
        conn.execute("REPLACE INTO app_settings (setting_name, setting_value) VALUES (?, ?)",
                     ('password_hash', generate_password_hash(new_password)))
        conn.commit()
        conn.close()

class LoginDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.setWindowTitle("Login")
        self.setModal(True)
        self.setFixedSize(300, 150)

        layout = QVBoxLayout()

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.check_login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def check_login(self):
        password = self.password_input.text()
        if self.db.check_password(password):
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid password.")
            self.password_input.clear()

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.db.init_database()

        # Attempt to log in
        login_dialog = LoginDialog(self.db, self)
        if login_dialog.exec_() == QDialog.Accepted:
            self.init_ui()
        else:
            sys.exit() # Exit application if login fails or is cancelled
        
    def init_ui(self):
        print("init_ui called")
        self.setWindowTitle("AAMUSTED Counselling Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create menu bar

class StudentDialog(QDialog):
    """Dialog for adding/editing students"""
    
    def __init__(self, parent=None, student_id=None):
        super().__init__(parent)
        self.student_id = student_id
        self.db = DatabaseManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Add Student" if not self.student_id else "Edit Student")
        self.setModal(True)
        self.resize(400, 500)
        
        layout = QFormLayout()
        
        # Form fields
        self.name_edit = QLineEdit()
        self.age_edit = QLineEdit()
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['Male', 'Female', 'Other'])
        self.programme_edit = QLineEdit()
        self.contact_edit = QLineEdit()
        self.index_edit = QLineEdit()
        self.department_edit = QLineEdit()
        self.faculty_edit = QLineEdit()
        self.parent_contact_edit = QLineEdit()
        self.hall_edit = QLineEdit()
        
        layout.addRow("Name:", self.name_edit)
        layout.addRow("Age:", self.age_edit)
        layout.addRow("Gender:", self.gender_combo)
        layout.addRow("Programme:", self.programme_edit)
        layout.addRow("Contact:", self.contact_edit)
        layout.addRow("Index Number:", self.index_edit)
        layout.addRow("Department:", self.department_edit)
        layout.addRow("Faculty:", self.faculty_edit)
        layout.addRow("Parent Contact:", self.parent_contact_edit)
        layout.addRow("Hall of Residence:", self.hall_edit)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        self.setLayout(layout)
        
        if self.student_id:
            self.load_student()
    
    def load_student(self):
        conn = self.db.get_connection()
        student = conn.execute('SELECT * FROM Student WHERE id = ?', (self.student_id,)).fetchone()
        conn.close()
        
        if student:
            self.name_edit.setText(student['name'])
            self.age_edit.setText(str(student['age']))
            self.gender_combo.setCurrentText(student['gender'])
            self.programme_edit.setText(student['programme'])
            self.contact_edit.setText(student['contact'])
            self.index_edit.setText(student['index_number'])
            self.department_edit.setText(student['department'])
            self.faculty_edit.setText(student['faculty'])
            self.parent_contact_edit.setText(student['parent_contact'] or '')
            self.hall_edit.setText(student['hall_of_residence'] or '')
    
    def get_data(self):
        return {
            'name': self.name_edit.text(),
            'age': int(self.age_edit.text()) if self.age_edit.text() else None,
            'gender': self.gender_combo.currentText(),
            'programme': self.programme_edit.text(),
            'contact': self.contact_edit.text(),
            'index_number': self.index_edit.text(),
            'department': self.department_edit.text(),
            'faculty': self.faculty_edit.text(),
            'parent_contact': self.parent_contact_edit.text(),
            'hall_of_residence': self.hall_edit.text()
        }

class SessionDialog(QDialog):
    """Dialog for adding/editing session notes"""

    def __init__(self, parent=None, session_id=None, appointment_id=None):
        super().__init__(parent)
        self.session_id = session_id
        self.appointment_id = appointment_id
        self.db = DatabaseManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Add Session Note" if not self.session_id else "Edit Session Note")
        self.setModal(True)
        self.resize(500, 400)

        layout = QFormLayout()

        self.session_date_edit = QDateEdit(calendarPopup=True)
        self.session_date_edit.setDate(QDate.currentDate())
        self.session_date_edit.setMinimumDate(QDate(2000, 1, 1))
        self.session_date_edit.setMaximumDate(QDate.currentDate())

        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Enter session notes...")

        self.outcome_edit = QTextEdit()
        self.outcome_edit.setPlaceholderText("Enter session outcome...")

        layout.addRow("Session Date:", self.session_date_edit)
        layout.addRow("Notes:", self.notes_edit)
        layout.addRow("Outcome:", self.outcome_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

        if self.session_id:
            self.load_session()

    def load_session(self):
        conn = self.db.get_connection()
        session = conn.execute('SELECT * FROM Session WHERE id = ?', (self.session_id,)).fetchone()
        conn.close()

        if session:
            self.session_date_edit.setDate(QDate.fromString(session['session_date'].split(' ')[0], 'yyyy-MM-dd'))
            self.notes_edit.setText(session['notes'])
            self.outcome_edit.setText(session['outcome'])
            self.appointment_id = session['appointment_id']

    def get_data(self):
        return {
            'session_date': self.session_date_edit.date().toString(Qt.ISODate),
            'notes': self.notes_edit.toPlainText(),
            'outcome': self.outcome_edit.toPlainText(),
            'appointment_id': self.appointment_id
        }

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        print("MainWindow __init__ called")
        self.db = DatabaseManager()
        self.db.init_database()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("AAMUSTED Counselling Management System")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create menu bar
        self.create_menu_bar()

        # Add a menu item for changing password
        settings_menu = self.menuBar().addMenu("Settings")
        change_password_action = settings_menu.addAction("Change Password")
        change_password_action.triggered.connect(self.change_password)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create individual tabs
        self.dashboard_tab = self.create_dashboard_tab()
        self.students_tab = self.create_students_tab()
        self.appointments_tab = self.create_appointments_tab()
        self.sessions_tab = self.create_sessions_tab()
        
        # Add tabs
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.students_tab, "Students")
        self.tabs.addTab(self.appointments_tab, "Appointments")
        self.tabs.addTab(self.sessions_tab, "Sessions")
        
        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        central_widget.setLayout(layout)
        
        # Set stylesheet for modern look
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 10px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QTableWidget {
                border: 1px solid #ddd;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 5px;
                border: 1px solid #ddd;
                font-weight: bold;
            }
        """)
        
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        exit_action = file_menu.addAction('Exit')
        exit_action.triggered.connect(self.close)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about)

    def change_password(self):
        new_password, ok = QInputDialog.getText(self, "Change Password", "Enter new password:", QLineEdit.Password)
        if ok and new_password:
            self.db.set_password(new_password)
            QMessageBox.information(self, "Password Changed", "Your password has been successfully updated.")
        elif ok:
            QMessageBox.warning(self, "Password Change Failed", "Password cannot be empty.")

    def show_about(self):
        QMessageBox.about(self, "About AAMUSTED Counselling Management System",
                          "This application helps manage student counselling records.")
    
    def create_dashboard_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("AAMUSTED Counselling Dashboard")
        header_label.setFont(QFont('Arial', 18, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        
        # Get stats
        conn = self.db.get_connection()
        total_students = conn.execute('SELECT COUNT(*) as count FROM Student').fetchone()['count']
        total_appointments = conn.execute('SELECT COUNT(*) as count FROM Appointment').fetchone()['count']
        today_appointments = conn.execute(
            "SELECT COUNT(*) as count FROM Appointment WHERE date = date('now')"
        ).fetchone()['count']
        conn.close()
        
        # Create stat cards
        self.create_stat_card(stats_layout, "Total Students", str(total_students))
        self.create_stat_card(stats_layout, "Total Appointments", str(total_appointments))
        self.create_stat_card(stats_layout, "Today's Appointments", str(today_appointments))
        
        layout.addLayout(stats_layout)
        
        # Recent appointments table
        recent_label = QLabel("Recent Appointments")
        recent_label.setFont(QFont('Arial', 14, QFont.Bold))
        layout.addWidget(recent_label)
        
        self.recent_table = QTableWidget()
        self.recent_table.setColumnCount(6)
        self.recent_table.setHorizontalHeaderLabels(['Date', 'Time', 'Student', 'Counsellor', 'Status', 'Purpose'])
        self.recent_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.recent_table)
        
        self.load_recent_appointments()
        
        widget.setLayout(layout)
        return widget
    
    def create_stat_card(self, layout, title, value):
        card = QGroupBox(title)
        card_layout = QVBoxLayout()
        
        value_label = QLabel(value)
        value_label.setFont(QFont('Arial', 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        
        card_layout.addWidget(value_label)
        card.setLayout(card_layout)
        layout.addWidget(card)
    
    def create_students_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_button = QPushButton("Add Student")
        add_button.clicked.connect(self.add_student)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.load_students)
        
        toolbar.addWidget(add_button)
        toolbar.addWidget(refresh_button)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Students table
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(6)
        self.students_table.setHorizontalHeaderLabels(['ID', 'Name', 'Index Number', 'Programme', 'Contact', 'Department'])
        self.students_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.students_table)
        
        self.load_students()
        
        widget.setLayout(layout)
        return widget
    
    def create_appointments_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        add_button = QPushButton("Add Appointment")
        refresh_button = QPushButton("Refresh")
        
        toolbar.addWidget(add_button)
        toolbar.addWidget(refresh_button)
        toolbar.addStretch()
        
        layout.addLayout(toolbar)
        
        # Appointments table
        self.appointments_table = QTableWidget()
        self.appointments_table.setColumnCount(6)
        self.appointments_table.setHorizontalHeaderLabels(['Date', 'Time', 'Student', 'Counsellor', 'Status', 'Purpose'])
        self.appointments_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.appointments_table)
        
        self.load_appointments()

        widget.setLayout(layout)
        return widget

    def create_sessions_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Toolbar
        toolbar = QHBoxLayout()

        add_session_button = QPushButton("Add Session")
        add_session_button.clicked.connect(self.add_session)

        refresh_sessions_button = QPushButton("Refresh Sessions")
        refresh_sessions_button.clicked.connect(self.load_sessions)

        toolbar.addWidget(add_session_button)
        toolbar.addWidget(refresh_sessions_button)
        toolbar.addStretch()

        layout.addLayout(toolbar)

        # Sessions table
        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(5) # ID, Date, Student, Notes, Outcome
        self.sessions_table.setHorizontalHeaderLabels(['ID', 'Date', 'Student', 'Notes', 'Outcome'])
        self.sessions_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.sessions_table)

        self.sessions_table.doubleClicked.connect(self.edit_session)

        self.load_sessions()

        widget.setLayout(layout)
        return widget

    def add_session(self):
        # First, let the user select an appointment
        conn = self.db.get_connection()
        appointments = conn.execute('''
            SELECT
                a.id,
                s.name AS student_name,
                a.date,
                a.time,
                a.purpose
            FROM Appointment a
            JOIN Student s ON a.student_id = s.id
            WHERE a.status = 'scheduled' OR a.status = 'completed'
            ORDER BY a.date DESC, a.time DESC
        ''').fetchall()
        conn.close()

        if not appointments:
            QMessageBox.warning(self, "No Appointments", "There are no scheduled or completed appointments to add a session to.")
            return

        appointment_options = []
        for appt in appointments:
            appointment_options.append(f"ID: {appt['id']} - {appt['student_name']} ({appt['date']} {appt['time']}) - {appt['purpose']}")

        item, ok = QInputDialog.getItem(self, "Select Appointment", "Choose an appointment for the session:", appointment_options, 0, False)

        if ok and item:
            selected_appointment_id = int(item.split(' - ')[0].replace('ID: ', ''))
            dialog = SessionDialog(self, appointment_id=selected_appointment_id)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                conn = self.db.get_connection()
                conn.execute("INSERT INTO Session (session_date, notes, outcome, appointment_id) VALUES (?, ?, ?, ?)",
                             (data['session_date'], data['notes'], data['outcome'], selected_appointment_id))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Session added successfully.")
                self.load_sessions()
                # Optionally update appointment status to 'completed' if it was 'scheduled'
                # conn = self.db.get_connection()
                # conn.execute("UPDATE Appointment SET status = 'completed' WHERE id = ? AND status = 'scheduled'", (selected_appointment_id,))
                # conn.commit()
                # conn.close()
                # self.load_appointments()

    def edit_session(self):
        selected_row = self.sessions_table.currentRow()
        if selected_row >= 0:
            session_id = int(self.sessions_table.item(selected_row, 0).text())
            dialog = SessionDialog(self, session_id=session_id)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_data()
                conn = self.db.get_connection()
                conn.execute("UPDATE Session SET session_date = ?, notes = ?, outcome = ? WHERE id = ?",
                             (data['session_date'], data['notes'], data['outcome'], session_id))
                conn.commit()
                conn.close()
                QMessageBox.information(self, "Success", "Session updated successfully.")
                self.load_sessions()

    def load_sessions(self):
        conn = self.db.get_connection()
        sessions = conn.execute('''
            SELECT
                s.id,
                s.created_at AS session_date,
                st.name AS student_name,
                s.notes,
                s.outcome
            FROM Session s
            JOIN Appointment a ON s.appointment_id = a.id
            JOIN Student st ON a.student_id = st.id
            ORDER BY s.session_date DESC
        ''').fetchall()
        conn.close()

        self.sessions_table.setRowCount(len(sessions))
        for row, session in enumerate(sessions):
            self.sessions_table.setItem(row, 0, QTableWidgetItem(str(session['id'])))
            self.sessions_table.setItem(row, 1, QTableWidgetItem(session['session_date'].split(' ')[0]))
            self.sessions_table.setItem(row, 2, QTableWidgetItem(session['student_name']))
            self.sessions_table.setItem(row, 3, QTableWidgetItem(session['notes']))
            self.sessions_table.setItem(row, 4, QTableWidgetItem(session['outcome']))
            for col in range(5):
                self.sessions_table.item(row, col).setFlags(self.sessions_table.item(row, col).flags() & ~Qt.ItemIsEditable)
        
        widget.setLayout(layout)
        return widget
    
    def load_students(self):
        conn = self.db.get_connection()
        students = conn.execute('''
            SELECT id, name, index_number, programme, contact, department 
            FROM Student ORDER BY created_at DESC
        ''').fetchall()
        conn.close()
        
        self.students_table.setRowCount(len(students))
        for row, student in enumerate(students):
            for col, value in enumerate(student):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.students_table.setItem(row, col, item)
    
    def load_appointments(self):
        conn = self.db.get_connection()
        appointments = conn.execute('''
            SELECT a.date, a.time, s.name as student_name, c.name as Counsellor_name, a.status, a.purpose
            FROM Appointment a
            JOIN Student s ON a.student_id = s.id
            JOIN Counsellor c ON a.Counsellor_id = c.id
            ORDER BY a.date DESC, a.time DESC
        ''').fetchall()
        conn.close()
        
        self.appointments_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments):
            for col, value in enumerate(appointment):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.appointments_table.setItem(row, col, item)
    
    def load_recent_appointments(self):
        conn = self.db.get_connection()
        appointments = conn.execute('''
            SELECT a.date, a.time, s.name as student_name, c.name as Counsellor_name, a.status, a.purpose
            FROM Appointment a
            JOIN Student s ON a.student_id = s.id
            JOIN Counsellor c ON a.Counsellor_id = c.id
            WHERE a.date >= date('now')
            ORDER BY a.date, a.time
            LIMIT 10
        ''').fetchall()
        conn.close()
        
        self.recent_table.setRowCount(len(appointments))
        for row, appointment in enumerate(appointments):
            for col, value in enumerate(appointment):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.recent_table.setItem(row, col, item)
    
    def add_student(self):
        dialog = StudentDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            conn = self.db.get_connection()
            conn.execute('''
                INSERT INTO Student (name, age, gender, programme, contact, 
                                   index_number, department, faculty, parent_contact, hall_of_residence)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (data['name'], data['age'], data['gender'], data['programme'],
                  data['contact'], data['index_number'], data['department'],
                  data['faculty'], data['parent_contact'], data['hall_of_residence']))
            conn.commit()
            conn.close()
            self.load_students()
            self.load_recent_appointments()
    
    def show_about(self):
        QMessageBox.about(self, "About", 
                         "AAMUSTED Counselling Management System\n\n"
                         "Version 2.0 - Desktop Edition\n"
                         "A native desktop application for managing\n"
                         "student counselling services at AAMUSTED.")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AAMUSTED Counselling System")
    
    # Set application icon if available
    if os.path.exists('icon.ico'):
        app.setWindowIcon(QIcon('icon.ico'))
    
    window = MainWindow()
    window.show()
    
    return app.exec_()

if __name__ == '__main__':
    sys.exit(main())