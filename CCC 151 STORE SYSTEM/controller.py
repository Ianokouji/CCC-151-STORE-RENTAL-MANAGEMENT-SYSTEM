from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem, QPushButton, QHBoxLayout, QWidget, QSizePolicy,QHeaderView,QDialog
from PyQt5 import QtCore 
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QStyleFactory, QTableWidgetItem
from ModifiedInterface import Ui_MainWindow 

from PyQt5.QtGui import QColor
from datetime import datetime

from updateTenant import EditTenantDialog
from TenantBill import BillDialog
from DeleteTenant import ConfirmationDialog
from updateUnit import EditStoreUnitDialog
from updatePayment import UpdatePaymentDialog
from DeletePayment import DeletePaymentsDialog
from updateRental import UpdateRentalDialog
from DeleteRental import DeleteRentalsDialog

from DeleteUnit import DeleteStoreUnitConfirmationDialog


from Operations import TenantOperations,StoreUnitOperations,PaymentOperations,RentalOperations


'''
    Contents:
            * Controller class that connects the operations to the User Interface
            * Utilizes qdialogs from separate files
            * Validates inputs and handles errors

    Definition for Unit Status in Units:
            * Default upon adding / no record in both rental and payment table - Vacant
            * If a Unit has a payment record or a rental record but not both -> Pending
            * If Payment Status in Payments Table is anything but not 'Paid' -> Pending
            * If present in both Rentals and Payments Table -> Occupied
    
    Special Cases:
            * If Start date is less than the current date -> Pending
            * If End date is greater than the current date -> Pending


AUTHORS:
        Angelyn Jimeno
        Hussam Bansao
        Ian Gabriel Paulmino

        
'''






class Controller:
    def __init__(self):
        self.app = QApplication([])

        # Create the main window
        self.main_window = QMainWindow()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self.main_window)
        

        # Initializes the operations classes
        self.Tenant_Operations = TenantOperations("localhost", "root", "2022-1729", "STORE_DATABASE")
        self.Unit_Operations = StoreUnitOperations("localhost", "root", "2022-1729", "STORE_DATABASE")
        self.Payment_Operations = PaymentOperations("localhost", "root", "2022-1729", "STORE_DATABASE")
        self.Rental_Operations = RentalOperations("localhost", "root", "2022-1729", "STORE_DATABASE")

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Button Connections 
        #self.ui.DashboardButton.clicked.connect(self.ChangeWidgetDashBoard)
        self.ui.TenantsButton.clicked.connect(self.ChangeWidgetTenants)
        self.ui.UnitsButton.clicked.connect(self.ChangeWidgetUnits)
        self.ui.PaymentsButton.clicked.connect(self.ChangeWidgetPayments)
        self.ui.RentalsButton.clicked.connect(self.ChangeWidgetRentals)
        self.ui.AddTenant.clicked.connect(self.addTenant)
        self.ui.SearchTenant.clicked.connect(self.SearchTenant)
        self.ui.SearchUnit.clicked.connect(self.SearchStoreUnit)
        self.ui.AddUnit.clicked.connect(self.AddStoreUnit)
        self.ui.AddPayment.clicked.connect(self.AddPayment)
        self.ui.SearchPayments.clicked.connect(self.SearchPayment)
        self.ui.AddRental.clicked.connect(self.AddRental)
        self.ui.SearchRentals.clicked.connect(self.SearchRental)

# -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





# Functionality for changing Stacked Widgets
    def ChangeWidgetLogin(self, index):
        self.ui.LoginStackedWidget.setCurrentIndex(index)

    def ChangeWidgetMain(self, index):
        self.ui.MainStackedWidget.setCurrentIndex(index)

    def ChangeWidgetTenants(self):
        self.ChangeWidgetMain(3)

    def ChangeWidgetUnits(self):
        self.ChangeWidgetMain(4)
    
    def ChangeWidgetPayments(self):
        self.ChangeWidgetMain(2)

    def ChangeWidgetRentals(self):
        self.ChangeWidgetMain(1)
    

    def ChangeWidgetDashBoard(self):
        self.ChangeWidgetMain(0)

    



# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# TENANT OPERATIONS
# ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    # Puts content the Tenants table with buttons
    def UpdateTenantsTable(self):
        tenants = self.Tenant_Operations.LoadTenants()
        self.ui.TenantsTable.setRowCount(0)  # Clear any existing rows

        # Ensure the table has enough columns to include the button widget
        num_columns = len(tenants[0]) + 1 if tenants else 1
        self.ui.TenantsTable.setColumnCount(num_columns)
        
        # Set column headers with "Operations" as the first column
        headers = ["OPERATIONS", "TENANT_ID", "TENANT_NAME", "EMAIL_ADRESSS", "CONTACT_NUMBER"]
        self.ui.TenantsTable.setHorizontalHeaderLabels(headers)

        for tenant in tenants:
            rowPosition = self.ui.TenantsTable.rowCount()
            self.ui.TenantsTable.insertRow(rowPosition)

            # Create buttons for edit, delete, and retrieve bill operations
            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")
            #retrieve_button = QPushButton("Bill")

            # Adjust button size policy and minimum size
            for button in (edit_button, delete_button):
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setMinimumSize(40, 20)  # Adjust the size as needed
                button.setMaximumSize(40, 20)

            # Connect buttons to their respective methods
            edit_button.clicked.connect(lambda _, row=rowPosition: self.editTenant(row))
            delete_button.clicked.connect(lambda _, row=rowPosition: self.deleteTenant(row))
            #retrieve_button.clicked.connect(lambda _, row=rowPosition: self.retrieveBill(row))

            # Create a widget to hold the buttons and add it to the table
            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            #button_layout.addWidget(retrieve_button)
            button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better fitting

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            # Add the buttons widget to the first column
            self.ui.TenantsTable.setCellWidget(rowPosition, 0, button_widget)

            # Insert tenant data into the table starting from the second column
            for col, data in enumerate(tenant):
                self.ui.TenantsTable.setItem(rowPosition, col + 1, QTableWidgetItem(str(data)))
            
        
        



    # Edits tenant and validates inputs
    # Manually updates the changes in the related tables 
    def editTenant(self, row):
        try:
            selected_row = row
            if selected_row >= 0:
                tenant_id = self.ui.TenantsTable.item(selected_row, 1).text()
                tenant_name = self.ui.TenantsTable.item(selected_row, 2).text()
                email_address = self.ui.TenantsTable.item(selected_row, 3).text()
                contact_number = self.ui.TenantsTable.item(selected_row, 4).text()

                
                # Open the edit dialog with the selected tenant's information
                dialog = EditTenantDialog(tenant_id, tenant_name, email_address, contact_number, parent=self.main_window)
                if dialog.exec_() == QDialog.Accepted:
                    # Dialog was accepted, get the updated tenant information
                    updated_info = dialog.getTenantInfo()

                    # Unpack updated_info into separate variables
                    updated_tenant_id = updated_info["TENANT_ID"]
                    updated_tenant_name = updated_info["TENANT_NAME"]
                    updated_email_address = updated_info["EMAIL_ADDRESS"]
                    updated_contact_number = updated_info["CONTACT_NUMBER"]

                    if updated_tenant_id and updated_tenant_name and updated_email_address and updated_contact_number:

                        if self.validateContactNumber(updated_contact_number) and self.validateTenantID(updated_tenant_id):

                            # Use updated_info to update the database or perform any other operations
                            success, error_message = self.Tenant_Operations.UpdateTenant(updated_tenant_id, updated_tenant_name, updated_email_address, updated_contact_number, tenant_id)

                            if success:
                                self.UpdateTenantsTable()
                                
                                # Update Payments Table manually
                                for i in range(self.ui.PaymentsTable.rowCount()):
                                    Tenant_ID_item = self.ui.PaymentsTable.item(i, 2)  # Get the course code item for the current student
                                    if Tenant_ID_item and Tenant_ID_item.text() == tenant_id:
                                        Tenant_ID_item.setText(updated_tenant_id)

                                # Update Payments Table manually
                                for i in range(self.ui.RentalsTable.rowCount()):
                                    Tenant_ID_item = self.ui.RentalsTable.item(i, 2)  # Get the course code item for the current student
                                    if Tenant_ID_item and Tenant_ID_item.text() == tenant_id:
                                        Tenant_ID_item.setText(updated_tenant_id)
                                
                                self.UpdateRentalsTenantID_ComboBox()
                                self.UpdatePaymentsTenantID_ComboBox()
                                QMessageBox.information(self.main_window, "Update Tenant", "Update successful")
                            else:
                                QMessageBox.critical(self.main_window, "Error", error_message)
                        else:
                            QMessageBox.critical(self.main_window, "Error", "Please input valid formats")
                    else:
                        QMessageBox.critical(self.main_window, "Edit Tenant Error", "Please fill in all the needed information")

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An unexpected error occurred: {e}")


        

    # Deletes a Tenant and manually removes rows related to that tenant on the Rentals and Payments table
    def deleteTenant(self, row):
        try:
            tenant_id = self.ui.TenantsTable.item(row, 1).text()
            confirmation_dialog = ConfirmationDialog(f"Are you sure you want to delete tenant with ID: {tenant_id}?", parent=self.main_window)
            if confirmation_dialog.exec_() == QDialog.Accepted:
                self.Tenant_Operations.DeleteTenant(tenant_id)

                UnitToUpdate = ""
                #self.UpdatePaymentsTable()
                # Delete existing rows in delete tenant
                for i in range(self.ui.PaymentsTable.rowCount() - 1, -1, -1):
                    Tenant_ID_item = self.ui.PaymentsTable.item(i, 2)  # Get the course code item for the current student
                    Unit_ID_item = self.ui.PaymentsTable.item(i, 1)
                    if Tenant_ID_item and Tenant_ID_item.text() == tenant_id:
                        UnitToUpdate = Unit_ID_item.text()
                        self.ui.PaymentsTable.removeRow(i)
                        

                # Delete existing rows in delete tenant
                for i in range(self.ui.RentalsTable.rowCount() - 1, -1, -1):
                    Tenant_ID_item = self.ui.RentalsTable.item(i, 2)  # Get the course code item for the current student
                    units_ID_item = self.ui.RentalsTable.item(i, 1)
                    if Tenant_ID_item and Tenant_ID_item.text() == tenant_id:
                        UnitToUpdate = units_ID_item.text()
                        self.ui.RentalsTable.removeRow(i)

                # Update Payments Table manually
                for i in range(self.ui.UnitsTable.rowCount()):
                    unit_ID_item = self.ui.UnitsTable.item(i, 1)  # Get the course code item for the current student
                    unit_status = self.ui.UnitsTable.item(i, 4)
                    if unit_ID_item.text() == UnitToUpdate:
                        #Tenant_ID_item.setText(updated_tenant_id)
                        unit_status.setText("Vacant")

                
                self.CountTenants()
                self.UpdatePaymentsTenantID_ComboBox()
                self.UpdateRentalsTenantID_ComboBox()
                self.UpdateTenantsTable()
                self.UpdateUnitsTable()
                # Update Units table manually


                QMessageBox.information(self.main_window, "Delete Tenant", "Tenant deleted successfully.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An unexpected error occurred: {e}")

    
    # Retrieves the bill of a tenant using the Payments Table Bill Button
    def retrieveBill(self, row):
        try:
            tenant_id = self.ui.PaymentsTable.item(row, 2).text()
            
            # Initialize variables to hold the total duration and unit price
            total_duration = 0
            unit_price = 0

            # Loop through the rentals table to find the tenant ID and calculate the total duration
            for rental_row in range(self.ui.RentalsTable.rowCount()):
                rental_tenant_id = self.ui.RentalsTable.item(rental_row, 2).text()
                if rental_tenant_id == tenant_id:
                    start_date = self.ui.RentalsTable.item(rental_row, 3).text()
                    end_date = self.ui.RentalsTable.item(rental_row, 4).text()
                    duration = self.calculate_duration(start_date, end_date)
                    total_duration += duration

                    unit_id = self.ui.RentalsTable.item(rental_row, 1).text()

                    # Find the unit price from the units table using the unit ID
                    for unit_row in range(self.ui.UnitsTable.rowCount()):
                        if self.ui.UnitsTable.item(unit_row, 1).text() == unit_id:  # Assuming unit ID is in the first column
                            unit_price = float(self.ui.UnitsTable.item(unit_row, 5).text())  # Assuming unit price is in the fifth column
                            break

            if total_duration > 0 and unit_price > 0:
                bill_amount = total_duration * unit_price
                # Create and show the BillDialog
                dialog = BillDialog(tenant_id, bill_amount, parent=self.main_window)
                dialog.exec_()
            else:
                QMessageBox.warning(self.main_window, "Error", f"Failed to retrieve bill for tenant with ID: {tenant_id}")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An unexpected error occurred: {e}")


    # Validates inputs and Adds a tenant 
    def addTenant(self):
        # Retrieve data from LineEdits
        tenant_id = self.ui.TenantID.text()
        tenant_name = self.ui.TenantName.text()
        email_address = self.ui.EmailAdd.text()
        contact_number = self.ui.ContactNum.text()

        # Check if contact number is in the correct format
        if not self.validateContactNumber(contact_number):
            QMessageBox.warning(self.main_window, "Error", "Contact number must be in the format: 000 0000 000")
            return
        
        # Check if tenant ID is in the correct format
        if not self.validateTenantID(tenant_id):
            QMessageBox.warning(self.main_window, "Error", "Tenant ID must be in the format: XXXX-XXXX")
            return
        
        if tenant_id and tenant_name and email_address and contact_number:

            # Call the helper function to add the tenant
            success, error_message = self.Tenant_Operations.AddTenant(tenant_id, tenant_name, email_address, contact_number)

            if success:
                self.ui.TenantID.clear()
                self.ui.TenantName.clear()
                self.ui.EmailAdd.clear()
                self.ui.ContactNum.clear()
                QMessageBox.information(self.main_window, "Add Tenant", "Tenant added successfully.")

                self.CountTenants()
                self.UpdateRentalsTenantID_ComboBox()
                self.UpdatePaymentsTenantID_ComboBox()
                self.UpdateTenantsTable()  # Update the table to reflect the new tenant
            else:
                QMessageBox.critical(self.main_window, "Error", error_message)
        else:
            QMessageBox.critical(self.main_window, "Add Tenant Error", "Please fill in all the needed information")


    # Validates the the format of the contact number
    def validateContactNumber(self, contact_number):
        # Implement your validation logic here
        # For example, you can check if the length is 12 and if it contains spaces at the correct positions
        if len(contact_number) != 12 or contact_number[3] != ' ' or contact_number[8] != ' ':
            return False
        return True


    # Validates the format of the Tenant ID
    def validateTenantID(self, tenant_id):
        # Check if tenant ID is in the format XXXX-XXXX
        if len(tenant_id) != 9:
            return False
        parts = tenant_id.split('-')
        if len(parts) != 2 or len(parts[0]) != 4 or len(parts[1]) != 4:
            return False
        if not all(part.isdigit() for part in parts):
            return False
        return True
    

    # Handles the search of a tenant using the ComboBox to set its modes
    def SearchTenant(self):
        search_mode = self.ui.SearchTenantComboBox.currentText()
        if search_mode == "Tenant Name":
            # Perform search by tenant name logic
            search_text = self.ui.SearchBarTenants.text()
            tenantsName = self.Tenant_Operations.SearchTenantName(search_text)
            self.DisplaySearchResults(tenantsName)
            # Update table or handle search results as needed
        elif search_mode == "Tenant ID":
            # Perform search by tenant ID logic
            search_text = self.ui.SearchBarTenants.text()
            tenantsID = self.Tenant_Operations.SearchTenantID(search_text)
            self.DisplaySearchResults(tenantsID)
            # Update table or handle search results as needed



    # Display results after search of a tenant
    def DisplaySearchResults(self, tenants):
        self.ui.TenantsTable.setRowCount(0)  # Clear existing rows

        if tenants:
            # Set column headers
            headers = ["OPERATIONS", "TENANT_ID", "TENANT_NAME", "EMAIL_ADRESSS", "CONTACT_NUMBER"]
            self.ui.TenantsTable.setHorizontalHeaderLabels(headers)

            for tenant in tenants:
                rowPosition = self.ui.TenantsTable.rowCount()
                self.ui.TenantsTable.insertRow(rowPosition)

                # Create buttons for edit, delete, and retrieve bill operations
                edit_button = QPushButton("Edit")
                delete_button = QPushButton("Delete")
                #retrieve_button = QPushButton("Bill")

                # Adjust button size policy and minimum size
                for button in (edit_button, delete_button):
                    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    button.setMinimumSize(40, 20)  # Adjust the size as needed
                    button.setMaximumSize(40, 20)

                # Connect buttons to their respective methods
                edit_button.clicked.connect(lambda _, row=rowPosition: self.editTenant(row))
                delete_button.clicked.connect(lambda _, row=rowPosition: self.deleteTenant(row))
                #retrieve_button.clicked.connect(lambda _, row=rowPosition: self.retrieveBill(row))

                # Create a widget to hold the buttons and add it to the table
                button_layout = QHBoxLayout()
                button_layout.addWidget(edit_button)
                button_layout.addWidget(delete_button)
                #button_layout.addWidget(retrieve_button)
                button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better fitting

                button_widget = QWidget()
                button_widget.setLayout(button_layout)

                # Add the buttons widget to the first column
                self.ui.TenantsTable.setCellWidget(rowPosition, 0, button_widget)

                # Insert tenant data into the table starting from the second column
                for col, data in enumerate(tenant):
                    self.ui.TenantsTable.setItem(rowPosition, col + 1, QTableWidgetItem(str(data)))

        else:
            QMessageBox.information(self.main_window, "Search Results", "No tenants found.")

    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # STORE UNITS OPERATIONS
    # ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------










    # Puts content the Tenants table with buttons
    def UpdateUnitsTable(self):
        Units = self.Unit_Operations.LoadStoreUnits()
        self.ui.UnitsTable.setRowCount(0)  # Clear any existing rows

        # Ensure the table has enough columns to include the button widget
        num_columns = len(Units[0]) + 1 if Units else 1
        self.ui.UnitsTable.setColumnCount(num_columns)
        
        # Set column headers with "Operations" as the first column
        headers = ["OPERATIONS", "UNIT_ID", "UNIT_NAME", "STORE_TYPE", "UNIT_STATUS" ,"UNIT_PRICE"]
        self.ui.UnitsTable.setHorizontalHeaderLabels(headers)

        for unit in Units:
            rowPosition = self.ui.UnitsTable.rowCount()
            self.ui.UnitsTable.insertRow(rowPosition)

            # Create buttons for edit and delete
            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")
            #retrieve_button = QPushButton("Bill")

            # Adjust button size policy and minimum size
            for button in (edit_button, delete_button):
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setMinimumSize(40, 20)  # Adjust the size as needed
                button.setMaximumSize(40, 20)

            # Connect buttons to their respective methods
            edit_button.clicked.connect(lambda _, row=rowPosition: self.EditStoreUnit(row))
            delete_button.clicked.connect(lambda _, row=rowPosition: self.DeleteStoreUnit(row))
            #retrieve_button.clicked.connect(lambda _, row=rowPosition: self.retrieveBill(row))

            # Create a widget to hold the buttons and add it to the table
            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            #button_layout.addWidget(retrieve_button)
            button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better fitting

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            # Add the buttons widget to the first column
            self.ui.UnitsTable.setCellWidget(rowPosition, 0, button_widget)

            # Insert tenant data into the table starting from the second column
            for col, data in enumerate(unit):
                self.ui.UnitsTable.setItem(rowPosition, col + 1, QTableWidgetItem(str(data)))
        self.LoadAvailableUnits()


    # Edits a Store Unit and validates inputs
    # Manually updates the changes in the related tables 
    def EditStoreUnit(self, row):
        try:
            selected_row = row
            if selected_row >= 0:
                unit_id = self.ui.UnitsTable.item(selected_row, 1).text()
                unit_name = self.ui.UnitsTable.item(selected_row, 2).text()
                store_type = self.ui.UnitsTable.item(selected_row, 3).text()
                unit_price = self.ui.UnitsTable.item(selected_row, 5).text()

                # Open the edit dialog with the selected unit's information
                dialog = EditStoreUnitDialog(unit_id, unit_name, store_type, unit_price, parent=self.main_window)
                if dialog.exec_() == QDialog.Accepted:
                    # Dialog was accepted, get the updated store unit information
                    updated_info = dialog.getStoreUnitInfo()

                    # Unpack updated_info into separate variables
                    updated_unit_id = updated_info["UNIT_ID"]
                    updated_unit_name = updated_info["UNIT_NAME"]
                    updated_store_type = updated_info["STORE_TYPE"]
                    updated_unit_price = updated_info["UNIT_PRICE"]


                    if updated_unit_id and updated_unit_name and updated_store_type and updated_unit_price:
                        if not self.validateUnitID(updated_unit_id):
                            QMessageBox.critical(self.main_window, "Error", "Unit ID Valid format is AAA-XXXX")
                            return
                        
                        #if not self.validateUnitPrice(updated_unit_price):
                            #QMessageBox.critical(self.main_window, "Error", "Unit price must not have: whitespace,commas and other special characters")
                            #return
                            
                        # Use updated_info to update the database or perform any other operations
                        success, error_message = self.Unit_Operations.UpdateStoreUnit(updated_unit_id, updated_unit_name, updated_store_type, updated_unit_price, unit_id)

                        if success:
                            self.UpdateUnitsTable()

                            # Update Payments Table manually
                            for i in range(self.ui.PaymentsTable.rowCount()):
                                Unit_ID_item = self.ui.PaymentsTable.item(i, 1)  # Get the course code item for the current student
                                if Unit_ID_item and Unit_ID_item.text() == unit_id:
                                    Unit_ID_item.setText(updated_unit_id)

                            for i in range(self.ui.RentalsTable.rowCount()):
                                Unit_ID_item = self.ui.RentalsTable.item(i, 1)  # Get the course code item for the current student
                                if Unit_ID_item and Unit_ID_item.text() == unit_id:
                                    Unit_ID_item.setText(updated_unit_id)

                            #self.UpdatePaymentsTable()
                            self.UpdatePaymentsUnitID_ComboBox()
                            self.UpdateRentalsUnitID_ComboBox()
                            QMessageBox.information(self.main_window, "Update Store Unit", "Update successful")
                        else:
                            QMessageBox.critical(self.main_window, "Error", error_message)
                    else:
                        QMessageBox.critical(self.main_window, "Edit StoreUnit Error","Please fill in the required information")
                    

        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An unexpected error occurred: {e}")


    # Deletes a Store Unit and manually removes rows related to that tenant on the Rentals and Payments table
    def DeleteStoreUnit(self, row):
        try:
            unit_id = self.ui.UnitsTable.item(row, 1).text()
            confirmation_dialog = DeleteStoreUnitConfirmationDialog(f"Are you sure you want to delete store unit with ID: {unit_id}?", parent=self.main_window)
            if confirmation_dialog.exec_() == QDialog.Accepted:
                self.Unit_Operations.DeleteStoreUnit(unit_id)

                TenantToDelete = ""
                #self.UpdatePaymentsTable()
                # Delete existing rows in delete tenant
                for i in range(self.ui.PaymentsTable.rowCount() - 1, -1, -1):
                    Tenant_ID_item = self.ui.PaymentsTable.item(i, 2)  # Get the course code item for the current student
                    Unit_ID_item = self.ui.PaymentsTable.item(i, 1)
                    if Unit_ID_item and Unit_ID_item.text() == unit_id:
                        TenantToDelete = Tenant_ID_item.text()
                        self.ui.PaymentsTable.removeRow(i)
                        

                # Delete existing rows in delete tenant
                for i in range(self.ui.RentalsTable.rowCount() - 1, -1, -1):
                    Tenant_ID_item = self.ui.RentalsTable.item(i, 2)  # Get the course code item for the current student
                    units_ID_item = self.ui.RentalsTable.item(i, 1)
                    if units_ID_item and units_ID_item.text() == unit_id:
                        TenantToDelete = Tenant_ID_item.text()
                        self.ui.RentalsTable.removeRow(i)

                # Delete existing rows in delete tenant
                for i in range(self.ui.TenantsTable.rowCount() - 1, -1, -1):
                    Tenant_ID_item = self.ui.TenantsTable.item(i, 1)  # Get the course code item for the current student
                    #units_ID_item = self.ui.RentalsTable.item(i, 1)
                    if Tenant_ID_item and Tenant_ID_item.text() == TenantToDelete:
                        self.ui.TenantsTable.removeRow(i)
    
                self.LoadAvailableUnits()
                self.CountUnits()
                self.UpdateUnitsTable()
                self.UpdatePaymentsUnitID_ComboBox()
                self.UpdateRentalsUnitID_ComboBox()
                QMessageBox.information(self.main_window, "Delete Store Unit", "Store unit deleted successfully.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An unexpected error occurred: {e}")

    
    # Validates the format of the UnitID
    def validateUnitID(self, unit_id):
        # Check if the ID format is XXX-XXXX where X is an alphanumeric character
        if len(unit_id) == 8 and unit_id[3] == '-':
            prefix = unit_id[:3]
            suffix = unit_id[4:]
            if prefix.isalpha() and suffix.isdigit():
                return True
        return False
    

     # Handles the search of a Store Unit using the ComboBox to set its modes
    def SearchStoreUnit(self):
        search_mode = self.ui.SearchUnitComboBox.currentText()
        if search_mode == "Unit Name":
            # Perform search by unit name logic
            search_text = self.ui.SearchBarUnit.text()
            unitsName = self.Unit_Operations.SearchStoreUnitName(search_text)
            self.DisplayUnitSearchResults(unitsName)
            # Update table or handle search results as needed
        elif search_mode == "Unit ID":
            # Perform search by unit ID logic
            search_text = self.ui.SearchBarUnit.text()
            unitsID = self.Unit_Operations.SearchStoreUnitID(search_text)
            self.DisplayUnitSearchResults(unitsID)
    

    # Display results after search of a Store Unit
    def DisplayUnitSearchResults(self, units):
        self.ui.UnitsTable.setRowCount(0)  # Clear existing rows

        if units:
            # Set column headers
            headers = ["OPERATIONS", "UNIT_ID", "UNIT_NAME", "STORE_TYPE", "UNIT_PRICE"]
            self.ui.UnitsTable.setHorizontalHeaderLabels(headers)

            for unit in units:
                rowPosition = self.ui.UnitsTable.rowCount()
                self.ui.UnitsTable.insertRow(rowPosition)

                # Create buttons for edit and delete operations
                edit_button = QPushButton("Edit")
                delete_button = QPushButton("Delete")

                # Adjust button size policy and minimum size
                for button in (edit_button, delete_button):
                    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    button.setMinimumSize(40, 20)  # Adjust the size as needed
                    button.setMaximumSize(40, 20)

                # Connect buttons to their respective methods
                edit_button.clicked.connect(lambda _, row=rowPosition: self.EditStoreUnit(row))
                delete_button.clicked.connect(lambda _, row=rowPosition: self.DeleteStoreUnit(row))

                # Create a widget to hold the buttons and add it to the table
                button_layout = QHBoxLayout()
                button_layout.addWidget(edit_button)
                button_layout.addWidget(delete_button)
                button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better fitting

                button_widget = QWidget()
                button_widget.setLayout(button_layout)

                # Add the buttons widget to the first column
                self.ui.UnitsTable.setCellWidget(rowPosition, 0, button_widget)

                # Insert unit data into the table starting from the second column
                for col, data in enumerate(unit):
                    self.ui.UnitsTable.setItem(rowPosition, col + 1, QTableWidgetItem(str(data)))

            # Adjust the size of the "Operations" column to fit the buttons
            # self.ui.UnitsTable.horizontalHeader().setSectionResizeMode(len(unit), QHeaderView.Stretch)
        else:
            QMessageBox.information(self.main_window, "Search Results", "No units found.")

    
    # Validates inputs and adds a Store Units 
    def AddStoreUnit(self):
        # Retrieve data from LineEdits
        Unit_id = self.ui.UnitID.text()
        Unit_name = self.ui.UnitName.text()
        Store_type = self.ui.StoreType.text()
        Unit_price = self.ui.UnitPrice.text()

        
        if Unit_id and Unit_name and Store_type and Unit_price:
            # Check if tenant ID is in the correct format
            if not self.validateUnitID(Unit_id):
                QMessageBox.warning(self.main_window, "Error", "Unit ID must be in the format: AAA-XXXX")
                return
            
                            
            
            # When Adding a Store Unit, it is vacant by default
            UnitStatus = "Vacant"

            # Call the helper function to add the tenant
            success, error_message = self.Unit_Operations.AddStoreUnit(Unit_id, Unit_name, Store_type,UnitStatus,Unit_price)

            if success:
                self.ui.UnitID.clear()
                self.ui.UnitName.clear()
                self.ui.StoreType.clear()
                self.ui.UnitPrice.clear()
                QMessageBox.information(self.main_window, "Add Store Unit", "Store Unit added successfully.")

                self.LoadAvailableUnits()
                self.CountUnits()
                self.UpdatePaymentsUnitID_ComboBox()
                self.UpdateUnitsTable()  # Update the table to reflect the new tenant
            else:
                QMessageBox.critical(self.main_window, "Error", error_message)
        else:
            QMessageBox.critical(self.main_window, "Add StoreUnit Error","Please fill in the required information")


    


    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Payments Operations
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    # Puts content the Payments table with buttons
    def UpdatePaymentsTable(self):
        Payments = self.Payment_Operations.LoadPayments()
        self.ui.PaymentsTable.setRowCount(0)  # Clear any existing rows

        # Ensure the table has enough columns to include the button widget
        num_columns = len(Payments[0]) + 1 if Payments else 1
        self.ui.PaymentsTable.setColumnCount(num_columns)

        # Set column headers with "Operations" as the first column
        headers = ["OPERATIONS", "UNIT_ID", "TENANT_ID", "PAYMENT_DATE", "PAYMENT_TYPE", "PAYMENT_STATUS"]
        self.ui.PaymentsTable.setHorizontalHeaderLabels(headers)

        for payment in Payments:
            rowPosition = self.ui.PaymentsTable.rowCount()
            self.ui.PaymentsTable.insertRow(rowPosition)

            # Create buttons for edit and delete
            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")
            retrieve_button = QPushButton("Bill")

            # Adjust button size policy and minimum size
            for button in (edit_button, delete_button,retrieve_button):
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setMinimumSize(40, 20)  # Adjust the size as needed
                button.setMaximumSize(40, 20)

            # Connect buttons to their respective methods
            edit_button.clicked.connect(lambda _, row=rowPosition: self.EditPayment(row))
            delete_button.clicked.connect(lambda _, row=rowPosition: self.DeletePayment(row))
            retrieve_button.clicked.connect(lambda _, row=rowPosition: self.retrieveBill(row))

            # Create a widget to hold the buttons and add it to the table
            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.addWidget(retrieve_button)
            button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better fitting

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            # Add the buttons widget to the first column
            self.ui.PaymentsTable.setCellWidget(rowPosition, 0, button_widget)

            # Insert payment data into the table starting from the second column
            for col, data in enumerate(payment):
                self.ui.PaymentsTable.setItem(rowPosition, col + 1, QTableWidgetItem(str(data)))
        

    # Edits the payment information
    # Sets the Unit status of a Unit depending on Inputs
    def EditPayment(self, row):
        try:
            selected_row = row
            if selected_row >= 0:
                
                Unit_id = self.ui.PaymentsTable.item(selected_row, 1).text()
                tenant_id = self.ui.PaymentsTable.item(selected_row, 2).text()
                payment_date = self.ui.PaymentsTable.item(selected_row, 3).text()
                payment_type = self.ui.PaymentsTable.item(selected_row, 4).text()
                payment_status = self.ui.PaymentsTable.item(selected_row, 5).text()
                

                # Open the edit dialog with the selected payment's information
                dialog = UpdatePaymentDialog(Unit_id, tenant_id, payment_date, payment_type, payment_status, parent=self.main_window)
                if dialog.exec_() == QDialog.Accepted:
                    # Dialog was accepted, get the updated payment information
                    updated_info = dialog.getPaymentInfo()

                    
                    updated_payment_date = updated_info["PAYMENT_DATE"]
                    updated_payment_type = updated_info["PAYMENT_TYPE"]
                    updated_payment_status = updated_info["PAYMENT_STATUS"]
                   
                    if updated_payment_date and updated_payment_type and updated_payment_status:
                        Payment_dateT = datetime.strptime(updated_payment_date, '%Y-%m-%d').date()
                        current_date = datetime.now().date()

                        if Payment_dateT > current_date:
                            QMessageBox.critical(self.main_window,"Edit Add Error","Payment Date must not be beyond current date")
                            return

                        # Use updated_info to update the database or perform any other operations
                        success, error_message = self.Payment_Operations.UpdatePayment(
                            Unit_id,
                            updated_payment_date, updated_payment_type, updated_payment_status
                        )

                        if success:
                            UnitStatus_Checker = 0
                            PaymentStatus_Checker = 0
                            if updated_payment_status == 'Paid':
                                PaymentStatus_Checker += 1    
                        
                                
                            CurrentStatus = ""
                            if PaymentStatus_Checker == 1:
                                CurrentStatus = "Occupied"
                            else:
                                CurrentStatus = "Pending"

                            # Update the UnitStatus in the UnitsTable
                            for i in range(self.ui.UnitsTable.rowCount()):
                                unit_id_itemT = self.ui.UnitsTable.item(i, 1)  # Assuming UnitID is in the first column
                                unit_status_item = self.ui.UnitsTable.item(i, 4)  # Assuming UnitStatus is in the fourth column

                                #if unit_id_itemT:
                                unit_id = unit_id_itemT.text()
                                if unit_id == Unit_id:  # Check if this unit matches the added payment's unit ID
                                    new_status = CurrentStatus
                                    unit_status_item.setText(new_status)
                                    break  # Exit the loop after updating the corresponding unit
                            
                            self.LoadAvailableUnits()
                            self.UpdatePaymentsTable()
                            QMessageBox.information(self.main_window, "Update Payment", "Update successful")
                        else:
                            QMessageBox.critical(self.main_window, "Error", error_message)
                    else:
                        QMessageBox.critical(self.main_window,"Edit Payment Error","Please fill in the required information")
                        
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An unexpected error occurred: {e}")

    

    
    # Deletes a payment
    # Updates the Unit status manually
    def DeletePayment(self,row):
        #QMessageBox.information(self.main_window, "Delete Payment", f"Delete on payment row {row}")
        try:
            Unit_id = self.ui.PaymentsTable.item(row, 1).text()
            confirmation_dialog = DeletePaymentsDialog(f"Are you sure you want to delete payment with ID: {Unit_id}?", parent=self.main_window)
            if confirmation_dialog.exec_() == QDialog.Accepted:
                self.Payment_Operations.DeletePayment(Unit_id)

                UnitStatus_Checker = 0
               

                # Iterate through the UnitsTable
                for i in range(self.ui.UnitsTable.rowCount()):
                    unit_id_item = self.ui.UnitsTable.item(i, 1)  # Assuming UnitID is in the second column
                    

                    if unit_id_item:
                        unit_id = unit_id_item.text()
                        if Unit_id == unit_id:
                            UnitStatus_Checker += 1

                # Iterate through the RentalsTable
                for i in range(self.ui.RentalsTable.rowCount()):
                    unit_id_item = self.ui.RentalsTable.item(i, 1)  # Assuming UnitID is in the second column

                    if unit_id_item:
                        unit_id = unit_id_item.text()
                        if Unit_id == unit_id:
                            UnitStatus_Checker += 1

                    
                        
                CurrentStatus = ""
                if UnitStatus_Checker == 2:
                    CurrentStatus = "Pending"
                elif UnitStatus_Checker == 1:
                    CurrentStatus = "Vacant"
                else:
                    CurrentStatus = "Occupied"

                # Update the UnitStatus in the UnitsTable
                for i in range(self.ui.UnitsTable.rowCount()):
                    unit_id_itemT = self.ui.UnitsTable.item(i, 1)  # Assuming UnitID is in the first column
                    unit_status_item = self.ui.UnitsTable.item(i, 4)  # Assuming UnitStatus is in the fourth column

                    #if unit_id_itemT:
                    unit_id = unit_id_itemT.text()
                    if unit_id == Unit_id:  # Check if this unit matches the added payment's unit ID
                        new_status = CurrentStatus
                        unit_status_item.setText(new_status)
                        break  # Exit the loop after updating the corresponding unit


                #self.UpdateUnitsTable()
                self.LoadAvailableUnits()
                self.UpdatePaymentsTenantID_ComboBox()
                self.UpdatePaymentsUnitID_ComboBox()
                self.UpdatePaymentsTable()
                QMessageBox.information(self.main_window, "Delete Payment", "Payment deleted successfully.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An unexpected error occurred: {e}")



    # Updates the Payments ComboBoxes for valid inputs
    def UpdatePaymentsUnitID_ComboBox(self):
        # Load all UnitIDs from the database using StoreUnitOperations
        unit_ids = self.Unit_Operations.LoadStoreUnits()
        
        # Clear existing items in the comboBox
        self.ui.UnitIDPayments.clear()
        payments  = self.Payment_Operations.LoadPayments()

        Used_Ids = []

        for unitID in payments:
            Used_Ids.append(unitID[0])

        # Add each UnitID to the comboBox
        for unit_id in unit_ids:
            if unit_id[0] not in Used_Ids:
                self.ui.UnitIDPayments.addItem(unit_id[0])
    
    def UpdatePaymentsTenantID_ComboBox(self):
        # Load all UnitIDs from the database using StoreUnitOperations
        tenant_ids = self.Tenant_Operations.LoadTenants()
        
        # Clear existing items in the comboBox
        self.ui.TenantIDPayments.clear()

        payments  = self.Payment_Operations.LoadPayments()

        Used_Ids = []

        for TenantID in payments:
            Used_Ids.append(TenantID[1])

        # Add each UnitID to the comboBox
        for tenant_id in tenant_ids:
            if tenant_id[0] not in Used_Ids:
               self.ui.TenantIDPayments.addItem(tenant_id[0])
    

    
    # Adds a payment
    # Updates the Unit Status manually
    def AddPayment(self):
        Unit_id = self.ui.UnitIDPayments.currentText()
        Tenant_id = self.ui.TenantIDPayments.currentText()
        Payment_date = self.ui.PaymentDate.text()
        Payment_type = self.ui.PaymentType.text()
        Payment_status = self.ui.PaymentStatus.text()


        if Unit_id and Tenant_id and Payment_date and Payment_type and Payment_status:

            Payment_dateT = datetime.strptime(Payment_date, '%Y-%m-%d').date()
            current_date = datetime.now().date()

            if Payment_dateT > current_date:
                QMessageBox.critical(self.main_window,"Edit Add Error","Payment Date must not be beyond current date")
                return
            

            #if both_exist_in_PaymentsTable or Does_Not_exist_in_PaymentsTable:
            does_not_exist_in_rentals_table = False
            both_exist_in_rentals_table = False
            either_one_exists_in_rentals_table = False

            UnitID_Rentals = []
            Tenant_id_Rentals = []
            # Check if the unit is not in the Rentals table
            for i in range(self.ui.RentalsTable.rowCount()):
                unit_id_item = self.ui.RentalsTable.item(i, 1)  # Assuming UnitID is in the second column
                tenant_id_item = self.ui.RentalsTable.item(i, 2)

                unitC_id = unit_id_item.text()
                tenantC_id = tenant_id_item.text()
                
                UnitID_Rentals.append(unitC_id)
                Tenant_id_Rentals.append(tenantC_id)

            if Unit_id not in UnitID_Rentals and Tenant_id not in Tenant_id_Rentals:
                does_not_exist_in_rentals_table = True

            
            # Check if both UnitID and TenantID exist together in the Payments table
            for i in range(self.ui.RentalsTable.rowCount()):
                unit_id_item = self.ui.RentalsTable.item(i, 1)
                tenant_id_item = self.ui.RentalsTable.item(i, 2)

                if unit_id_item and unit_id_item.text() == Unit_id:
                    # Get the entire row
                    row_data = []
                    for column in range(self.ui.RentalsTable.columnCount()):
                        item = self.ui.RentalsTable.item(i, column)
                        row_data.append(item.text() if item else "")
                    

                    if row_data[1] == Unit_id and row_data[2] == Tenant_id:
                        both_exist_in_rentals_table = True
                        break

                    
                    
            

            # Adjusted logic for allowing a new TenantID if either one exists in the Rentals table
            if does_not_exist_in_rentals_table:
                # New TenantID and UnitID are not in the Rentals table
                
                pass
            elif both_exist_in_rentals_table:
                # Both UnitID and TenantID exist together in the Rentals table
                
                pass
            else:
                # Neither condition above is met, so we assume either one exists in the Rentals table
                either_one_exists_in_rentals_table = True
            


            
            
            if not either_one_exists_in_rentals_table:
                success, error_message = self.Payment_Operations.AddPayment(Unit_id, Tenant_id, Payment_date, Payment_type, Payment_status)
                
                if success:
                    UnitStatus_Checker = 1
                    PaymentStatus_Checker = 0

                                
                    # Iterate through the RentalsTable
                    for i in range(self.ui.RentalsTable.rowCount()):
                        unit_id_item = self.ui.RentalsTable.item(i, 1)  # Assuming UnitID is in the second column

                        if unit_id_item:
                            unit_id = unit_id_item.text()
                            if Unit_id == unit_id:
                                UnitStatus_Checker += 1


                    
                    if Payment_status == 'Paid':
                        PaymentStatus_Checker += 1    
                    
                            
                    CurrentStatus = ""
                    if UnitStatus_Checker == 2 and PaymentStatus_Checker == 1:
                        CurrentStatus = "Occupied"
                    elif UnitStatus_Checker == 1:
                        CurrentStatus = "Pending"
                    else:
                        CurrentStatus = "Vacant"

                    # Update the UnitStatus in the UnitsTable
                    for i in range(self.ui.UnitsTable.rowCount()):
                        unit_id_itemT = self.ui.UnitsTable.item(i, 1)  # Assuming UnitID is in the first column
                        unit_status_item = self.ui.UnitsTable.item(i, 4)  # Assuming UnitStatus is in the fourth column

                        #if unit_id_itemT:
                        unit_id = unit_id_itemT.text()
                        if unit_id == Unit_id:  # Check if this unit matches the added payment's unit ID
                            new_status = CurrentStatus
                            unit_status_item.setText(new_status)
                            break  # Exit the loop after updating the corresponding unit

                    self.ui.PaymentDate.clear()
                    self.ui.PaymentType.clear()
                    self.ui.PaymentStatus.clear()
                    QMessageBox.information(self.main_window, "Add Payment", "Payment added successfully.")

                    
                    self.LoadAvailableUnits()
                    self.UpdatePaymentsTable()  # Update the table to reflect the new payment
                    self.UpdatePaymentsTenantID_ComboBox()
                    self.UpdatePaymentsUnitID_ComboBox()
                else:
                    QMessageBox.critical(self.main_window, "Error", error_message)
            else:
                QMessageBox.critical(self.main_window, "Add Payments Error", "Transactions must be consistent")
        else:
            QMessageBox.critical(self.main_window,"Add Payment Error","Please fill in the required information")



    # Handles the search of a Payment using the ComboBox to set its modes
    def SearchPayment(self):
        search_mode = self.ui.SearchPaymentsComboBox.currentText()
        if search_mode == "Tenant Name":
            # Perform search by tenant name logic
            search_text = self.ui.SearchBarPayments.text()
            tenantsName = self.Payment_Operations.SearchPaymentTenantName(search_text)
            self.DisplayPaymentsSearchResults(tenantsName)
            # Update table or handle search results as needed
        elif search_mode == "Unit Name":
            # Perform search by tenant ID logic
            search_text = self.ui.SearchBarPayments.text()
            UnitName = self.Payment_Operations.SearchPaymentUnitName(search_text)
            self.DisplayPaymentsSearchResults(UnitName)
            # Update table or handle search results as needed
        elif search_mode == 'Tenant ID':
            search_text = self.ui.SearchBarPayments.text()
            TenantID = self.Payment_Operations.SearchPaymentTenantID(search_text)
            self.DisplayPaymentsSearchResults(TenantID)
        elif search_mode == 'Unit ID':
            search_text = self.ui.SearchBarPayments.text()
            UnitID = self.Payment_Operations.SearchPaymentUnitID(search_text)
            self.DisplayPaymentsSearchResults(UnitID)
        
    
    
    # Display results after search of a Payment
    def DisplayPaymentsSearchResults(self, payments):
        self.ui.PaymentsTable.setRowCount(0)  # Clear any existing rows

        if payments:
            # Ensure the table has enough columns to include the button widget
            num_columns = len(payments[0]) + 1 if payments else 1
            self.ui.PaymentsTable.setColumnCount(num_columns)

            # Set column headers with "Operations" as the first column
            headers = ["OPERATIONS", "UNIT_ID", "TENANT_ID", "PAYMENT_DATE", "PAYMENT_TYPE", "PAYMENT_STATUS"]
            self.ui.PaymentsTable.setHorizontalHeaderLabels(headers)

            for payment in payments:
                rowPosition = self.ui.PaymentsTable.rowCount()
                self.ui.PaymentsTable.insertRow(rowPosition)

                # Create buttons for edit and delete
                edit_button = QPushButton("Edit")
                delete_button = QPushButton("Delete")

                # Adjust button size policy and minimum size
                for button in (edit_button, delete_button):
                    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    button.setMinimumSize(40, 20)  # Adjust the size as needed
                    button.setMaximumSize(40, 20)

                # Connect buttons to their respective methods
                edit_button.clicked.connect(lambda _, row=rowPosition: self.EditPayment(row))
                delete_button.clicked.connect(lambda _, row=rowPosition: self.DeletePayment(row))

                # Create a widget to hold the buttons and add it to the table
                button_layout = QHBoxLayout()
                button_layout.addWidget(edit_button)
                button_layout.addWidget(delete_button)
                button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better fitting

                button_widget = QWidget()
                button_widget.setLayout(button_layout)

                # Add the buttons widget to the first column
                self.ui.PaymentsTable.setCellWidget(rowPosition, 0, button_widget)

                # Insert payment data into the table starting from the second column
                for col, data in enumerate(payment):
                    self.ui.PaymentsTable.setItem(rowPosition, col + 1, QTableWidgetItem(str(data)))
        else:
            QMessageBox.information(self.main_window, "Search Results", "No payments found.")

    # --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Rentals Operations
    # ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


    # Calculates the exact duration for start and end dates 
    def calculate_duration(self,start_date, end_date):
        date_format = "%Y-%m-%d"  # Adjust the date format based on your data
        start = datetime.strptime(start_date, date_format)
        end = datetime.strptime(end_date, date_format)
        
        # Calculate duration in months
        duration = (end.year - start.year) * 12 + (end.month - start.month)
        return duration



    # Puts content the Rentals table with buttons
    def UpdateRentalsTable(self):
        Rentals = self.Rental_Operations.LoadRentals()  # Load the rental data from the database
        self.ui.RentalsTable.setRowCount(0)  # Clear any existing rows

        # Ensure the table has enough columns to include the button widget and duration
        num_columns = len(Rentals[0]) + 2 if Rentals else 2
        self.ui.RentalsTable.setColumnCount(num_columns)

        # Set column headers with "Operations" as the first column and "Duration" as the last
        headers = ["OPERATIONS", "UNIT_ID", "TENANT_ID", "START_DATE", "END_DATE", "DURATION"]
        self.ui.RentalsTable.setHorizontalHeaderLabels(headers)

        for rental in Rentals:
            rowPosition = self.ui.RentalsTable.rowCount()
            self.ui.RentalsTable.insertRow(rowPosition)

            # Create buttons for edit and delete
            edit_button = QPushButton("Edit")
            delete_button = QPushButton("Delete")

            # Adjust button size policy and minimum size
            for button in (edit_button, delete_button):
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.setMinimumSize(40, 20)  # Adjust the size as needed
                button.setMaximumSize(40, 20)

            # Connect buttons to their respective methods
            edit_button.clicked.connect(lambda _, row=rowPosition: self.EditRental(row))
            delete_button.clicked.connect(lambda _, row=rowPosition: self.DeleteRental(row))

            # Create a widget to hold the buttons and add it to the table
            button_layout = QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better fitting

            button_widget = QWidget()
            button_widget.setLayout(button_layout)

            # Add the buttons widget to the first column
            self.ui.RentalsTable.setCellWidget(rowPosition, 0, button_widget)

            # Insert rental data into the table starting from the second column
            for col, data in enumerate(rental):
                self.ui.RentalsTable.setItem(rowPosition, col + 1, QTableWidgetItem(str(data)))

            # Calculate and insert the duration into the last column
            start_date = rental[2]
            end_date = rental[3]
            duration = self.calculate_duration(start_date, end_date)
            self.ui.RentalsTable.setItem(rowPosition, len(rental) + 1, QTableWidgetItem(str(duration)))


    
    # Edits the Rental information
    # Changes the Unit Status depending on specific conditions
    # If StartDate is greater than the current date -> Pending | Tenant has not started yet
    # If EndDate is less than the current date -> Pending | Tenant has already finished renting
    def EditRental(self, row):
        try:
            selected_row = row
            if selected_row >= 0:
                
                Unit_id = self.ui.RentalsTable.item(selected_row, 1).text()
                tenant_id = self.ui.RentalsTable.item(selected_row, 2).text()
                start_date = self.ui.RentalsTable.item(selected_row, 3).text()
                end_date = self.ui.RentalsTable.item(selected_row, 4).text()

                # Open the edit dialog with the selected rental's information
                dialog = UpdateRentalDialog(Unit_id, tenant_id, start_date, end_date, parent=self.main_window)
                if dialog.exec_() == QDialog.Accepted:
                    # Dialog was accepted, get the updated rental information
                    updated_info = dialog.getRentalInfo()

                    updated_start_date = updated_info["START_DATE"]
                    updated_end_date = updated_info["END_DATE"]

                    # Use updated_info to update the database or perform any other operations
                    success, error_message = self.Rental_Operations.UpdateRental(
                        Unit_id,
                        updated_start_date, updated_end_date
                    )

                    if success:

                        UnitStatus_Checker = 1
                        PaymentStatus_Checker = 0

                        # Convert Start_date and End_date to datetime objects for comparison
                        start_date_obj = datetime.strptime(updated_start_date, '%Y-%m-%d').date()
                        end_date_obj = datetime.strptime(updated_end_date, '%Y-%m-%d').date()
                        current_date = datetime.now().date()

                        # Check if start date and end date are both greater than the current date
                        if start_date_obj > current_date and end_date_obj > current_date:
                            CurrentStatus = "Pending"

                        else:
                                                                    
                            # Iterate through the RentalsTable
                            for i in range(self.ui.PaymentsTable.rowCount()):
                                unit_id_item = self.ui.PaymentsTable.item(i, 1)  # Assuming UnitID is in the second column

                                if unit_id_item:
                                    unit_id = unit_id_item.text()
                                    if Unit_id == unit_id:
                                        UnitStatus_Checker += 1
                                        break

                            # Iterate throught the Payments Table
                            for i in range(self.ui.PaymentsTable.rowCount()):
                                unit_id_item = self.ui.PaymentsTable.item(i, 1)  # Assuming UnitID is in the second column
                                payment_status_item = self.ui.PaymentsTable.item(i, 5)  # Assuming PaymentStatus is in the fifth column

                                if unit_id_item:
                                    unit_id = unit_id_item.text()
                                    if Unit_id == unit_id:
                                        payment_status = payment_status_item.text() if payment_status_item else ''
                                        # Check if the payment status is 'Paid'
                                        if payment_status == 'Paid':
                                            PaymentStatus_Checker += 1
                                        
                            
                                    
                            CurrentStatus = ""
                            if UnitStatus_Checker == 2 and PaymentStatus_Checker == 1:
                                CurrentStatus = "Occupied"
                            elif UnitStatus_Checker == 1:
                                CurrentStatus = "Pending"
                            else:
                                CurrentStatus = "Vacant"

                        # Update the UnitStatus in the UnitsTable
                        for i in range(self.ui.UnitsTable.rowCount()):
                            unit_id_itemT = self.ui.UnitsTable.item(i, 1)  # Assuming UnitID is in the first column
                            unit_status_item = self.ui.UnitsTable.item(i, 4)  # Assuming UnitStatus is in the fourth column

                            #if unit_id_itemT:
                            unit_id = unit_id_itemT.text()
                            if unit_id == Unit_id:  # Check if this unit matches the added payment's unit ID
                                new_status = CurrentStatus
                                unit_status_item.setText(new_status)
                                
                                break 

                        self.LoadAvailableUnits()
                        self.UpdateRentalsTable()
                        QMessageBox.information(self.main_window, "Update Rental", "Update successful")
                    else:
                        QMessageBox.critical(self.main_window, "Error", error_message)
                        
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An unexpected error occurred: {e}")

    # Deletes a specific rental 
    def DeleteRental(self, row):
        try:
            Unit_id = self.ui.RentalsTable.item(row, 1).text()
            confirmation_dialog = DeleteRentalsDialog(f"Are you sure you want to delete rental with ID: {Unit_id}?", parent=self.main_window)
            if confirmation_dialog.exec_() == QDialog.Accepted:
                self.Rental_Operations.DeleteRental(Unit_id)

                UnitStatus_Checker = 0

                # Iterate through the UnitsTable
                for i in range(self.ui.UnitsTable.rowCount()):
                    unit_id_item = self.ui.UnitsTable.item(i, 1)  # Assuming UnitID is in the second column

                    if unit_id_item:
                        unit_id = unit_id_item.text()
                        if Unit_id == unit_id:
                            UnitStatus_Checker += 1

                # Iterate through the PaymentsTable
                for i in range(self.ui.PaymentsTable.rowCount()):
                    unit_id_item = self.ui.PaymentsTable.item(i, 1)  # Assuming UnitID is in the second column

                    if unit_id_item:
                        unit_id = unit_id_item.text()
                        if Unit_id == unit_id:
                            UnitStatus_Checker += 1

                CurrentStatus = ""
                if UnitStatus_Checker == 2:
                    CurrentStatus = "Pending"
                elif UnitStatus_Checker == 1:
                    CurrentStatus = "Vacant"
                else:
                    CurrentStatus = "Occupied"

                # Update the UnitStatus in the UnitsTable
                for i in range(self.ui.UnitsTable.rowCount()):
                    unit_id_itemT = self.ui.UnitsTable.item(i, 1)  # Assuming UnitID is in the first column
                    unit_status_item = self.ui.UnitsTable.item(i, 4)  # Assuming UnitStatus is in the fourth column

                    if unit_id_itemT:
                        unit_id = unit_id_itemT.text()
                        if unit_id == Unit_id:  # Check if this unit matches the deleted rental's unit ID
                            unit_status_item.setText(CurrentStatus)
                            break  # Exit the loop after updating the corresponding unit

                self.LoadAvailableUnits()
                self.UpdateRentalsTable()
                self.UpdateRentalsTenantID_ComboBox()
                self.UpdateRentalsUnitID_ComboBox()  
                QMessageBox.information(self.main_window, "Delete Rental", "Rental deleted successfully.")
        except Exception as e:
            QMessageBox.critical(self.main_window, "Error", f"An unexpected error occurred: {e}")


    # Updates the Payments ComboBoxes for valid inputs
    def UpdateRentalsUnitID_ComboBox(self):
        # Load all UnitIDs from the database using StoreUnitOperations
        unit_ids = self.Unit_Operations.LoadStoreUnits()
        
        # Clear existing items in the comboBox
        self.ui.UnitIDRentals.clear()
        rentals  = self.Rental_Operations.LoadRentals()

        Used_Ids = []

        for unitID in rentals:
            Used_Ids.append(unitID[0])

        # Add each UnitID to the comboBox
        for unit_id in unit_ids:
            if unit_id[0] not in Used_Ids:
                self.ui.UnitIDRentals.addItem(unit_id[0])
    
    def UpdateRentalsTenantID_ComboBox(self):
        # Load all UnitIDs from the database using StoreUnitOperations
        tenant_ids = self.Tenant_Operations.LoadTenants()
        
        # Clear existing items in the comboBox
        self.ui.TenantIDRentals.clear()

        rentals  = self.Rental_Operations.LoadRentals()

        Used_Ids = []

        for TenantID in rentals:
            Used_Ids.append(TenantID[1])

        # Add each UnitID to the comboBox
        for tenant_id in tenant_ids:
            if tenant_id[0] not in Used_Ids:
               self.ui.TenantIDRentals.addItem(tenant_id[0])


    # Adds a Rental after validating inputs
    # Manually updates the Unit Status
    def AddRental(self):
        Unit_id = self.ui.UnitIDRentals.currentText()
        Tenant_id = self.ui.TenantIDRentals.currentText()
        Start_date = self.ui.StartDate.text()
        End_date = self.ui.ContactNum_2.text()

        
        #if both_exist_in_PaymentsTable or Does_Not_exist_in_PaymentsTable:
        does_not_exist_in_payments_table = False
        both_exist_in_payments_table = False
        either_one_exists_in_payments_table = False

        UnitID_Payments = []
        Tenant_id_Payments = []
        # Check if the unit is not in the Payments table
        for i in range(self.ui.PaymentsTable.rowCount()):
            unit_id_item = self.ui.PaymentsTable.item(i, 1)  # Assuming UnitID is in the second column
            tenant_id_item = self.ui.PaymentsTable.item(i, 2)

            unitC_id = unit_id_item.text()
            tenantC_id = tenant_id_item.text()
            
            UnitID_Payments.append(unitC_id)
            Tenant_id_Payments.append(tenantC_id)

        if Unit_id not in UnitID_Payments and Tenant_id not in Tenant_id_Payments:
            does_not_exist_in_payments_table = True

        
        # Check if both UnitID and TenantID exist together in the Payments table
        for i in range(self.ui.PaymentsTable.rowCount()):
            unit_id_item = self.ui.PaymentsTable.item(i, 1)
            tenant_id_item = self.ui.PaymentsTable.item(i, 2)

            if unit_id_item and unit_id_item.text() == Unit_id:
                # Get the entire row
                row_data = []
                for column in range(self.ui.PaymentsTable.columnCount()):
                    item = self.ui.PaymentsTable.item(i, column)
                    row_data.append(item.text() if item else "")
                

                if row_data[1] == Unit_id and row_data[2] == Tenant_id:
                    both_exist_in_payments_table = True
                    break
                        

        # Adjusted logic for allowing a new TenantID if either one exists in the Payments table
        if does_not_exist_in_payments_table:
            # New TenantID and UnitID are not in the Payments table
              
            pass
        elif both_exist_in_payments_table:
            # Both UnitID and TenantID exist together in the Payments table
              
            pass
        else:
            # Neither condition above is met, so we assume either one exists in the Payments table
            either_one_exists_in_payments_table = True
           


        
        
        if not either_one_exists_in_payments_table:        
            success, error_message = self.Rental_Operations.AddRental(Unit_id, Tenant_id, Start_date, End_date)
            
            if success:
                UnitStatus_Checker = 1
                PaymentStatus_Checker = 0

                # Convert Start_date and End_date to datetime objects for comparison
                start_date_obj = datetime.strptime(Start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(End_date, '%Y-%m-%d').date()
                current_date = datetime.now().date()

                # Check if start date and end date are both greater than the current date
                if start_date_obj > current_date and end_date_obj > current_date:
                    CurrentStatus = "Pending"

                else:

                              
                    # Iterate through the RentalsTable
                    for i in range(self.ui.PaymentsTable.rowCount()):
                        unit_id_item = self.ui.PaymentsTable.item(i, 1)  # Assuming UnitID is in the second column

                        if unit_id_item:
                            unit_id = unit_id_item.text()
                            if Unit_id == unit_id:
                                UnitStatus_Checker += 1
                                break

                    # Iterate throught the Payments Table
                    for i in range(self.ui.PaymentsTable.rowCount()):
                        unit_id_item = self.ui.PaymentsTable.item(i, 1)  # Assuming UnitID is in the second column
                        payment_status_item = self.ui.PaymentsTable.item(i, 5)  # Assuming PaymentStatus is in the fifth column

                        if unit_id_item:
                            unit_id = unit_id_item.text()
                            if Unit_id == unit_id:
                                payment_status = payment_status_item.text() if payment_status_item else ''
                                # Check if the payment status is 'Paid'
                                if payment_status == 'Paid':
                                    PaymentStatus_Checker += 1
                                
                    
                            
                    CurrentStatus = ""
                    if UnitStatus_Checker == 2 and PaymentStatus_Checker == 1:
                        CurrentStatus = "Occupied"
                    elif UnitStatus_Checker == 1:
                        CurrentStatus = "Pending"
                    else:
                        CurrentStatus = "Vacant"

                # Update the UnitStatus in the UnitsTable
                for i in range(self.ui.UnitsTable.rowCount()):
                    unit_id_itemT = self.ui.UnitsTable.item(i, 1)  # Assuming UnitID is in the first column
                    unit_status_item = self.ui.UnitsTable.item(i, 4)  # Assuming UnitStatus is in the fourth column

                    #if unit_id_itemT:
                    unit_id = unit_id_itemT.text()
                    if unit_id == Unit_id:  # Check if this unit matches the added payment's unit ID
                        new_status = CurrentStatus
                        unit_status_item.setText(new_status)
                        break  # Exit the loop after updating the corresponding unit
                self.ui.StartDate.clear()
                # Was not renamed
                self.ui.ContactNum_2.clear()
                self.UpdateRentalsTenantID_ComboBox()
                self.UpdateRentalsUnitID_ComboBox()    
                QMessageBox.information(self.main_window, "Add Rental", "Rental added successfully.")
                
                
                self.LoadAvailableUnits()
                self.UpdateRentalsTable()  # Update the table to reflect the new rental
            else:
                QMessageBox.critical(self.main_window, "Error", error_message)
        else:
            QMessageBox.critical(self.main_window, "Add Rentals Error", "Transcations must be consistent")


     # Handles the search of a Rental using the ComboBox to set its modes
    def SearchRental(self):
        search_mode = self.ui.SearchRentalsComboBox.currentText()
        if search_mode == "Tenant Name":
            # Perform search by tenant name logic
            search_text = self.ui.SearchBarRentals.text()
            tenantsName = self.Rental_Operations.SearchRentalTenantName(search_text)
            self.DisplayRentalSearchResults(tenantsName)
            # Update table or handle search results as needed
        elif search_mode == "Unit Name":
            # Perform search by tenant ID logic
            search_text = self.ui.SearchBarRentals.text()
            UnitName = self.Rental_Operations.SearchRentalUnitName(search_text)
            self.DisplayRentalSearchResults(UnitName)
            # Update table or handle search results as needed
        elif search_mode == 'Tenant ID':
            search_text = self.ui.SearchBarRentals.text()
            TenantID = self.Rental_Operations.SearchRentalTenantID(search_text)
            self.DisplayRentalSearchResults(TenantID)
        elif search_mode == 'Unit ID':
            search_text = self.ui.SearchBarRentals.text()
            UnitID = self.Rental_Operations.SearchRentalUnitID(search_text)
            self.DisplayRentalSearchResults(UnitID)


    # Display results after search of a Rental
    def DisplayRentalSearchResults(self, rentals):
        self.ui.RentalsTable.setRowCount(0)  # Clear any existing rows

        if rentals:
            # Ensure the table has enough columns to include the button widget and duration
            num_columns = len(rentals[0]) + 2 if rentals else 2
            self.ui.RentalsTable.setColumnCount(num_columns)

            # Set column headers with "Operations" as the first column and "Duration" as the last
            headers = ["OPERATIONS", "UNIT_ID", "TENANT_ID", "START_DATE", "END_DATE", "DURATION"]
            self.ui.RentalsTable.setHorizontalHeaderLabels(headers)

            for rental in rentals:
                rowPosition = self.ui.RentalsTable.rowCount()
                self.ui.RentalsTable.insertRow(rowPosition)

                # Create buttons for edit and delete
                edit_button = QPushButton("Edit")
                delete_button = QPushButton("Delete")

                # Adjust button size policy and minimum size
                for button in (edit_button, delete_button):
                    button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                    button.setMinimumSize(40, 20)  # Adjust the size as needed
                    button.setMaximumSize(40, 20)

                # Connect buttons to their respective methods
                edit_button.clicked.connect(lambda _, row=rowPosition: self.EditRental(row))
                delete_button.clicked.connect(lambda _, row=rowPosition: self.DeleteRental(row))

                # Create a widget to hold the buttons and add it to the table
                button_layout = QHBoxLayout()
                button_layout.addWidget(edit_button)
                button_layout.addWidget(delete_button)
                button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for better fitting

                button_widget = QWidget()
                button_widget.setLayout(button_layout)

                # Add the buttons widget to the first column
                self.ui.RentalsTable.setCellWidget(rowPosition, 0, button_widget)

                # Insert rental data into the table starting from the second column
                for col, data in enumerate(rental):
                    self.ui.RentalsTable.setItem(rowPosition, col + 1, QTableWidgetItem(str(data)))

                # Calculate and insert the duration into the last column
                start_date = rental[2]
                end_date = rental[3]
                duration = self.calculate_duration(start_date, end_date)
                self.ui.RentalsTable.setItem(rowPosition, len(rental) + 1, QTableWidgetItem(str(duration)))
        else:
            QMessageBox.information(self.main_window, "Search Results", "No rentals found.")

    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # Dashboard Functions
    # -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    
    # Updater for the Total Tenants Count
    def CountTenants(self):
        all_tenants = 0
        tenants = self.Tenant_Operations.LoadTenants()
        for tenant in tenants:
            all_tenants += 1
        
        stringTenants = str(all_tenants)
        self.ui.TotalTenants.setText(stringTenants)

    # Updater for the Total Units Count
    def CountUnits(self):
        all_Units = 0
        units = self.Unit_Operations.LoadStoreUnits()
        for unit in units:
            all_Units += 1
        
        stringUnits = str(all_Units)
        self.ui.TotalUnits.setText(stringUnits)

    # Updater for the total Vacant Store Units
    def LoadAvailableUnits(self):
        #AvailableUnits = 0
        #print(self.ui.UnitsTable.rowCount())
        AvailableUnits = 0

        for i in range(self.ui.UnitsTable.rowCount()):
            # Assuming UnitStatus is in the 5th column (index 4)
            unit_status_item = self.ui.UnitsTable.item(i, 4)

            if unit_status_item is not None:  # Check if the item is not None
                unit_status = unit_status_item.text()
                if unit_status == 'Vacant':
                    AvailableUnits += 1
        self.ui.AvailableUnits.setText(str(AvailableUnits))
    
        


    # Functions that run immidiately after running the program
    def run(self):
        
        self.LoadAvailableUnits()
        self.CountUnits()
        self.CountTenants()
        self.UpdateRentalsTenantID_ComboBox()
        self.UpdateRentalsUnitID_ComboBox()
        self.UpdateRentalsTable()
        self.UpdatePaymentsTenantID_ComboBox()
        self.UpdatePaymentsUnitID_ComboBox()
        self.UpdatePaymentsTable()
        self.UpdateUnitsTable()
        self.UpdateTenantsTable()
        self.ChangeWidgetLogin(1)  # Change to the login widget initially
        self.ChangeWidgetMain(3)
        self.main_window.show()
        self.app.exec_()

    


if __name__ == "__main__":
    QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    QApplication.setStyle(QStyleFactory.create("Fusion"))
    controller = Controller()
    controller.run()


