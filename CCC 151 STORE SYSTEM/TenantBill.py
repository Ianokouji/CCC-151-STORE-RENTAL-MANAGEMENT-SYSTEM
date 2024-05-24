from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class BillDialog(QDialog):
    def __init__(self, tenant_id, bill_amount, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Tenant Bill")
        self.resize(300, 200)

        # Apply stylesheet
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: #000000;
                border: 2px solid #000000;
                border-radius: 10px;
            }
            QLabel {
                font-size: 12px;
                color: #333333;
            }
            QPushButton {
                background-color: #000000;
                color: #ffffff;
                border: none;
                border-radius: 4px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
            #titleLabel {
                font-size: 16px;
                font-weight: bold;
                color: #000000;
                padding: 10px;
            }
        """)

        # Font settings
        title_font = QFont("Arial", 16, QFont.Bold)
        label_font = QFont("Arial", 12)

        # Title label
        title_label = QLabel("Tenant Bill")
        title_label.setObjectName("titleLabel")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        # Create a layout for the dialog
        layout = QVBoxLayout()

        # Add labels to display tenant ID and bill amount
        tenant_id_label = QLabel(f"Tenant ID: {tenant_id}")
        tenant_id_label.setFont(label_font)
        bill_amount_label = QLabel(f"Bill Amount: ₱{bill_amount}")
        bill_amount_label.setFont(label_font)

        # Add a close button
        close_button = QPushButton("Close")
        close_button.setFont(label_font)
        close_button.clicked.connect(self.accept)

        # Add widgets to the layout
        layout.addWidget(title_label)
        layout.addWidget(tenant_id_label)
        layout.addWidget(bill_amount_label)
        layout.addStretch()
        layout.addWidget(close_button)

        # Set the layout for the dialog
        self.setLayout(layout)