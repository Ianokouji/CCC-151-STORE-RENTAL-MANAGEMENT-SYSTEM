from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class ConfirmationDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirmation")
        self.setFixedSize(450, 150)  # Set a fixed size for the dialog

        # Apply stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #000000;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #333333;
                padding: 10px;
            }
            QPushButton {
                background-color: #000000;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #003366;
            }
            #titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
            }
        """)

        # Font settings
        title_font = QFont("Arial", 16, QFont.Bold)
        label_font = QFont("Arial", 14)

        # Title label
        title_label = QLabel("Confirmation")
        title_label.setObjectName("titleLabel")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        # Message label
        message_label = QLabel(message)
        message_label.setFont(label_font)
        message_label.setAlignment(Qt.AlignCenter)

        # Buttons
        confirm_button = QPushButton("Confirm")
        confirm_button.setFont(label_font)
        confirm_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        confirm_button.clicked.connect(self.accept)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFont(label_font)
        cancel_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        cancel_button.clicked.connect(self.reject)

        # Layout for the dialog
        layout = QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(message_label)

        # Spacer item to push buttons to the bottom right
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        button_layout = QHBoxLayout()  # Horizontal layout for buttons
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)