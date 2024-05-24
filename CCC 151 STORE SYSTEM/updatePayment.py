from PyQt5.QtWidgets import QLineEdit, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class UpdatePaymentDialog(QDialog):
    def __init__(self, unit_id, tenant_id, payment_date, payment_type, payment_status, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Payment")
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
        bold_label_font = QFont("Arial", 12, QFont.Bold)  # New bold font for labels
        input_font = QFont("Arial", 11)

        # Title label
        title_label = QLabel("UPDATE PAYMENT")
        title_label.setObjectName("titleLabel")
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)

        # Labels for payment information
        unit_id_label = QLabel("Unit ID:")
        unit_id_label.setFont(label_font)
        tenant_id_label = QLabel("Tenant ID:")
        tenant_id_label.setFont(label_font)
        payment_date_label = QLabel("Payment Date:")
        payment_date_label.setFont(label_font)
        payment_type_label = QLabel("Payment Type:")
        payment_type_label.setFont(label_font)
        payment_status_label = QLabel("Payment Status:")
        payment_status_label.setFont(label_font)

        # Line edits for payment information
        self.payment_date_edit = QLineEdit(payment_date)
        self.payment_date_edit.setFont(input_font)
        self.payment_type_edit = QLineEdit(payment_type)
        self.payment_type_edit.setFont(input_font)
        self.payment_status_edit = QLineEdit(payment_status)
        self.payment_status_edit.setFont(input_font)

        # Labels for actual values (bolded)
        unit_id_value_label = QLabel("<b>{}</b>".format(unit_id))
        unit_id_value_label.setFont(bold_label_font)
        tenant_id_value_label = QLabel("<b>{}</b>".format(tenant_id))
        tenant_id_value_label.setFont(bold_label_font)

        # Layout for payment information
        info_layout = QVBoxLayout()
        self.addLabelAndEdit(info_layout, unit_id_label, unit_id_value_label, label_font)
        self.addLabelAndEdit(info_layout, tenant_id_label, tenant_id_value_label, label_font)
        self.addLabelAndEdit(info_layout, payment_date_label, self.payment_date_edit, label_font)
        self.addLabelAndEdit(info_layout, payment_type_label, self.payment_type_edit, label_font)
        self.addLabelAndEdit(info_layout, payment_status_label, self.payment_status_edit, label_font)

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

        # Variable to store payment info
        self.payment_info = None

    def addLabelAndEdit(self, layout, label, edit, font):
        label_layout = QHBoxLayout()
        label_layout.addWidget(label)
        label_layout.addWidget(edit)
        layout.addLayout(label_layout)

    def accept(self):
        # Get the updated payment information from line edits
        self.payment_info = {
            "PAYMENT_DATE": self.payment_date_edit.text(),
            "PAYMENT_TYPE": self.payment_type_edit.text(),
            "PAYMENT_STATUS": self.payment_status_edit.text()
        }
        super().accept()

    def getPaymentInfo(self):
        # Return the payment info
        return self.payment_info