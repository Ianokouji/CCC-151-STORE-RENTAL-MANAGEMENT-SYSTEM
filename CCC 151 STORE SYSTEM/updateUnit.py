from PyQt5.QtWidgets import QLineEdit, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class EditStoreUnitDialog(QDialog):
    def __init__(self, unit_id, unit_name, store_type, unit_price, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Store Unit")
        self.resize(400, 350)

        # Set a balanced theme with dark accents and black borders
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
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #000000;
                border-radius: 4px;
                padding: 5px;
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
        input_font = QFont("Arial", 11)

        # Title label
        title_label = QLabel("EDIT STORE UNIT")
        title_label.setObjectName("titleLabel")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        # Line edits for store unit information
        self.id_edit = QLineEdit(unit_id)
        self.id_edit.setFont(input_font)
        self.name_edit = QLineEdit(unit_name)
        self.name_edit.setFont(input_font)
        self.type_edit = QLineEdit(store_type)
        self.type_edit.setFont(input_font)
        self.price_edit = QLineEdit(unit_price)
        self.price_edit.setFont(input_font)

        # Layout for line edits
        info_layout = QVBoxLayout()
        self.addLabelAndEdit(info_layout, "Unit ID:", self.id_edit, label_font)
        self.addLabelAndEdit(info_layout, "Unit Name:", self.name_edit, label_font)
        self.addLabelAndEdit(info_layout, "Store Type:", self.type_edit, label_font)
        self.addLabelAndEdit(info_layout, "Unit Price:", self.price_edit, label_font)

        # Button layout
        button_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.setFont(label_font)
        cancel_button.setFont(label_font)
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)

        # Main layout for the dialog
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addLayout(info_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Connect buttons to methods
        save_button.clicked.connect(self.accept)  # Close the dialog and return QDialog.Accepted
        cancel_button.clicked.connect(self.reject)  # Close the dialog without saving

        # Variable to store store unit info
        self.store_unit_info = None

    def addLabelAndEdit(self, layout, label_text, edit, font):
        label_layout = QHBoxLayout()
        label = QLabel(label_text)
        label.setFont(font)
        label_layout.addWidget(label)
        label_layout.addWidget(edit)
        layout.addLayout(label_layout)

    def accept(self):
        # Get the updated store unit information from line edits
        self.store_unit_info = {
            "UNIT_ID": self.id_edit.text(),
            "UNIT_NAME": self.name_edit.text(),
            "STORE_TYPE": self.type_edit.text(),
            "UNIT_PRICE": self.price_edit.text()
        }
        super().accept()

    def getStoreUnitInfo(self):
        # Return the store unit info
        return self.store_unit_info