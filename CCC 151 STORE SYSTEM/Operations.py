import mysql.connector
from mysql.connector import errorcode

import datetime as dt
from datetime import datetime

import re


'''
Content:

    * Operations that handle the connections between database and python
    * Functionality for CRUDL operations on: Tenants, Store Units
      and how the are related using the Payments and Rentals     
'''



# Initializing connection for Database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2022-1729",
    database="STORE_DATABASE"
)

# Cursor for database connector
mycursor = db.cursor()





# Operations class that handles CRUDL for Tenants
class TenantOperations:
    def __init__(self, host, user, password, database) -> None:
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        self.mycursor = self.mydb.cursor()

    # Gets the contents of the tenants table
    def LoadTenants(self):
        self.mycursor.execute("SELECT * FROM TENANTS")
        tenants = self.mycursor.fetchall()  # Fetch all rows from the result set
        return tenants
        #for tenant in tenants:
            #print(tenant)
    
    # Updates the selected tenant
    def UpdateTenant(self,TenantId,TenantName,EmailAdd,ContactNum,TenantId_old):
        try:
            sqlUpdateTenant = ("CALL UpdateTenant(%s,%s,%s,%s,%s)")
            values_update_tenant = (TenantId,TenantName,EmailAdd,ContactNum,TenantId_old)
            self.mycursor.execute(sqlUpdateTenant,values_update_tenant)
            self.mydb.commit()

            return True,""

        except mysql.connector.Error as e:
            if e.errno == errorcode.ER_DUP_ENTRY:
                print(f"Error: Duplicate entry for TenantId: {TenantId}")
                error_message = f"Duplicate Entry for TenantId: {TenantId}"
            else:
                print(f"An error has occured during insertion: {e}")
                error_message = f"An error has occured during insertion: {e}"

            return False,error_message

    # Deletes the selected tenant
    def DeleteTenant(self,TenantId):
        sqlDeleteTenant = ("Call DeleteTenant(%s)")
        value_to_delete = (TenantId,)

        self.mycursor.execute(sqlDeleteTenant,value_to_delete)
        self.mydb.commit()


    # Inserts a new tenant to the tenant table
    def AddTenant(self,TenantId,TenantName,EmailAdd,ContactNum):
        try:
            sqlAddTenant = ("INSERT INTO TENANTS(TenantId,TenantName,EmailAdd,ContactNum) VALUES (%s,%s,%s,%s)")
            value_to_add = (TenantId,TenantName,EmailAdd,ContactNum)
            self.mycursor.execute(sqlAddTenant,value_to_add)
            self.mydb.commit()
            
            return True,""

        except mysql.connector.Error as e:
            if e.errno == errorcode.ER_DUP_ENTRY:
                print(f"Error: Duplicate entry for TenantId: {TenantId}")
                error_message = f"Duplicate Entry for TenantId: {TenantId}"
            else:
                print(f"An error has occured during insertion: {e}")
                error_message = f"An error has occured during insertion: {e}"

            return False,error_message

    # Seearch the tenants table using Tenant ID
    def SearchTenantID(self,TenantId):
        sqlSearchTenant = ("SELECT * FROM TENANTS WHERE TenantId LIKE %s")

        value_to_search = f"%{TenantId}%"
        
        self.mycursor.execute(sqlSearchTenant,(value_to_search,))
        tenants = self.mycursor.fetchall()
        return tenants
        #for tenant in tenants:
            #print(tenant)

    # Seearch the tenants table using Tenant Name
    def SearchTenantName(self,TenantName):
        sqlSearchTenant = ("SELECT * FROM TENANTS WHERE TenantName LIKE %s")

        value_to_search = f"%{TenantName}%"
        
        self.mycursor.execute(sqlSearchTenant,(value_to_search,))
        tenants = self.mycursor.fetchall()
        return tenants
    


    # Gets the Bill of a specific tenant
    def GetBill(self,TenantId):
        try:
            sqlGetTenantBill = """
                SELECT
                    r.StartDate,
                    r.EndDate,
                    u.UnitPrice
                FROM
                    rentals r
                INNER JOIN STOREUNITS u ON r.UnitId = u.UnitId
                WHERE
                    r.TenantId = %s
            """
            self.mycursor.execute(sqlGetTenantBill, (TenantId,))
            rental_info = self.mycursor.fetchone()

            if rental_info:
                start_date, end_date, unit_price = rental_info
                duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                print(f"Duration in months: {duration_months}")
                print(f"Unit price as float: {float(unit_price)}")
                bill_amount = duration_months * float(unit_price)
                print(f"Calculated bill amount: {bill_amount}")  # Debug output
                return True, bill_amount
            else:
                return False, "Tenant not found or has no rental information."

        except mysql.connector.Error as e:
            print(f"An error occurred while fetching bill: {e}")
            return False, f"Error: {e}"
        

    # Gets the bill of all tenants that has one
    def GetBillTotal(self,TenantId):
        try:
            sqlGetTenantBill = """
                SELECT
                    r.StartDate,
                    r.EndDate,
                    u.UnitPrice,
                    p.PaymentStatus
                FROM
                    rentals r
                INNER JOIN STOREUNITS u ON r.UnitId = u.UnitId
                INNER JOIN PAYMENTS p ON r.UnitId = p.UnitId
                WHERE
                    r.TenantId = %s
            """
            self.mycursor.execute(sqlGetTenantBill, (TenantId,))
            rental_info = self.mycursor.fetchone()

            if rental_info:
                start_date, end_date, unit_price, payment_status = rental_info
                if payment_status == 'Paid':
                    duration_months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
                    print(f"Duration in months: {duration_months}")
                    print(f"Unit price as float: {float(unit_price)}")
                    bill_amount = duration_months * float(unit_price)
                    print(f"Calculated bill amount: {bill_amount}")  # Debug output
                    return True, bill_amount
                else:
                    #return False, "Tenant has unpaid rentals."
                    pass
            else:
                #return False, "Tenant not found or has no rental information."
                pass

        except mysql.connector.Error as e:
            print(f"An error occurred while fetching bill: {e}")
            return False, f"Error: {e}"
        
        


# Operations class that handles CRUDL for StoreUnits
class StoreUnitOperations:
    def __init__(self, host, user, password, database) -> None:
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        self.mycursor = self.mydb.cursor()

    # Gets the contents of the Units table
    def LoadStoreUnits(self):
        self.mycursor.execute("SELECT * FROM STOREUNITS")
        StoreUnits = self.mycursor.fetchall()  # Fetch all rows from the result set
        return StoreUnits
        #for store in StoreUnits:
            #print(store)


    # Gets the count of available StoreUnits
    def LoadAvailableUnits(self):
        self.mycursor.execute("SELECT COUNT(*) FROM STOREUNITS WHERE UnitStatus = 'Vacant' ")
        StoreUnits = self.mycursor.fetchone()[0]   # Fetch all rows from the result set
        return StoreUnits


    # Updates a selected Store Unit
    def UpdateStoreUnit(self,UnitId,UnitName,StoreType,UnitPrice,UnitId_old):
        try:
            sqlUpdateStoreUnit = ("CALL UpdateUnit(%s,%s,%s,%s,%s)")
            values_update_storeunit = (UnitId,UnitName,StoreType,UnitPrice,UnitId_old)
            self.mycursor.execute(sqlUpdateStoreUnit,values_update_storeunit)
            self.mydb.commit()

            return True,""

        except mysql.connector.Error as e:
            if e.errno == errorcode.ER_DUP_ENTRY:
                print(f"Error: Duplicate entry for TenantId: {UnitId}")
                error_message = f"Duplicate Entry for TenantId: {UnitId}"
            else:
                print(f"An error has occured during insertion: {e}")
                error_message = f"An error has occured during insertion: {e}"

            return False,error_message


    # Inserts a new Store Unit to the Store Units table
    def AddStoreUnit(self,UnitId,UnitName,StoreType,UnitStatus,UnitPrice):
        try:
            sqlAddUnit = ("INSERT INTO STOREUNITS(UnitId, UnitName, StoreType,UnitStatus,UnitPrice) VALUES (%s,%s,%s,%s,%s)")
            value_to_add = (UnitId,UnitName,StoreType,UnitStatus,UnitPrice)
            self.mycursor.execute(sqlAddUnit,value_to_add)
            self.mydb.commit()
            
            return True,""

        except mysql.connector.Error as e:
            if e.errno == errorcode.ER_DUP_ENTRY:
                print(f"Error: Duplicate entry for UnitId: {UnitId}")
                error_message = f"Duplicate Entry for UnitId: {UnitId}"
            else:
                print(f"An error has occured during insertion: {e}")
                error_message = f"An error has occured during insertion: {e}"

            return False,error_message
        
    
    # Deletes a selected Store Unit
    def DeleteStoreUnit(self,UnitId):
        sqlDeleteUnit = ("Call DeleteUnit(%s)")
        value_to_delete = (UnitId,)

        self.mycursor.execute(sqlDeleteUnit,value_to_delete)
        self.mydb.commit()


    # Searches a Store Unit using Store Unit Id
    def SearchStoreUnitID(self,UnitId):
        sqlSearchUnit = ("SELECT * FROM STOREUNITS WHERE UnitId LIKE %s")

        value_to_search = f"%{UnitId}%"
        
        self.mycursor.execute(sqlSearchUnit,(value_to_search,))
        StoreUnits = self.mycursor.fetchall()
        return StoreUnits
        #for store in StoreUnits:
            #print(store)
    

     # Searches a Store Unit using Store Unit Name
    def SearchStoreUnitName(self,UnitName):
        sqlSearchUnit = ("SELECT * FROM STOREUNITS WHERE UnitName LIKE %s")

        value_to_search = f"%{UnitName}%"
        
        self.mycursor.execute(sqlSearchUnit,(value_to_search,))
        StoreUnits = self.mycursor.fetchall()
        return StoreUnits





# Operations class that handles CRUDL for Payments
class PaymentOperations:
    def __init__(self, host, user, password, database) -> None:
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        self.mycursor = self.mydb.cursor()


    
    # Helper function to validate dates 
    def ValidateDate(self,date):
        date_format = r"\d{4}-\d{2}-\d{2}"
        if re.match(date_format,date):
            return True
        else:
            return False


    # Gets the contents of the Paymetns table
    def LoadPayments(self):
        self.mycursor.execute("SELECT * FROM PAYMENTS")
        payments = self.mycursor.fetchall()

        formatted_payments = []  # Initialize an empty list to store formatted payments

        for payment in payments:
            formatted_payment = []
            for item in payment:
                if isinstance(item, dt.date):
                    formatted_payment.append(item.strftime("%Y-%m-%d"))
                else:
                    formatted_payment.append(item)
            formatted_payments.append(formatted_payment)  # Append each formatted payment to the list

        return formatted_payments  
    

    # Adds a new payment to the Payments table
    def AddPayment(self,UnitId,TenantId,PaymentDate,PaymentType,PaymentStatus):

        try:
            if self.ValidateDate(PaymentDate):
                #formatted_payment_date = self.FormatDate(PaymentDate)

                sqlAddPayment = ("INSERT INTO PAYMENTS(UnitId, TenantId, PaymentDate, PaymentType, PaymentStatus) VALUES (%s,%s,%s,%s,%s)")
                value_to_add = (UnitId,TenantId,PaymentDate,PaymentType,PaymentStatus)
                self.mycursor.execute(sqlAddPayment,value_to_add)
                self.mydb.commit()
            
                return True,""
            else:
                raise ValueError("Invalid PaymentDate format. Please enter a date in YYYY-MM-DD format.")
            
        except ValueError as ve:
            error_message = str(ve)
            print(error_message)
            return False,error_message

        except mysql.connector.Error as sqle:
            if sqle.errno == errorcode.ER_DUP_ENTRY:
                print("Error: A Tenant can only rent one Unit and vice versa")
                error_message = "Error: A Tenant can only rent one Unit and vice versa"
                return False, error_message
            
            else:
                print(f"MySQL Error: {sqle}")
                error_message = f"MySQL Error: {sqle}"
                return False, error_message
        
            

        except Exception as e:
            error_message = f"Error Adding Payments {e}"
            print(error_message)
            return False,error_message
        
    
    # Deletes Selected payment
    def DeletePayment(self,UnitId):
        sqlDeletePayment = "DELETE FROM PAYMENTS WHERE UnitId = %s"
        value_to_delete = (UnitId,)
        self.mycursor.execute(sqlDeletePayment,value_to_delete)
        self.mydb.commit()

    
    # Updates a selected Payment
    def UpdatePayment(self,UnitId,PaymentDate,PaymentType,PaymentStatus):
        try:
            if self.ValidateDate(PaymentDate):
                sqlUpdatePayment = "UPDATE PAYMENTS SET PaymentDate = %s, PaymentType = %s, PaymentStatus = %s WHERE UnitId = %s"
                value_to_update = (PaymentDate,PaymentType,PaymentStatus,UnitId)
                self.mycursor.execute(sqlUpdatePayment,value_to_update)
                self.mydb.commit()

                return True,""
            else:
                raise ValueError("Invalid PaymentDate format. Please enter a date in YYYY-MM-DD format.")
            
        except ValueError as ve:
            error_message = str(ve)
            print(error_message)
            return False,error_message
        
        except Exception as e:
            error_message = f"Error Adding Payments {e}"
            print(error_message)
            return False,error_message


    # Serachs a payment using the the Tenant Name 
    def SearchPaymentTenantName(self,TenantName):

        sqlSearchTenantPayment = "SELECT P.UnitId, P.TenantId, P.PaymentDate,P.PaymentType,P.PaymentStatus FROM PAYMENTS P INNER JOIN TENANTS T ON P.TenantId = T.TenantId WHERE T.TenantName LIKE %s"
        value_to_search = f"%{TenantName}%"
        self.mycursor.execute(sqlSearchTenantPayment,(value_to_search,))
        
        TenantPayment = self.mycursor.fetchall()

        formatted_payments = []

        for payment in TenantPayment:
            formated_payments = []
            for item in payment:
                if isinstance(item,dt.date):
                    formated_payments.append(item.strftime("%Y-%m-%d"))
                else:
                    formated_payments.append(item)
            formatted_payments.append(formated_payments)

            #print(formated_payments)
        return formatted_payments
    
    # Serachs a payment using the the Unit Name 
    def SearchPaymentUnitName(self,UnitName):

        sqlSearchTenantPayment = "SELECT P.UnitId, P.TenantId, P.PaymentDate,P.PaymentType,P.PaymentStatus FROM PAYMENTS P INNER JOIN STOREUNITS S ON P.UnitId = S.UnitId WHERE S.UnitName LIKE %s"
        value_to_search = f"%{UnitName}%"
        self.mycursor.execute(sqlSearchTenantPayment,(value_to_search,))
        
        TenantPayment = self.mycursor.fetchall()

        formatted_payments = []

        for payment in TenantPayment:
            formated_payments = []
            for item in payment:
                if isinstance(item,dt.date):
                    formated_payments.append(item.strftime("%Y-%m-%d"))
                else:
                    formated_payments.append(item)
            formatted_payments.append(formated_payments)
            
            #print(formated_payments)
        return formatted_payments
    
    # Serachs a payment using the the StoreUnit ID
    def SearchPaymentUnitID(self,UnitId):
        sqlSearchUnit = ("SELECT * FROM PAYMENTS WHERE UnitId LIKE %s")

        value_to_search = f"%{UnitId}%"
        
        self.mycursor.execute(sqlSearchUnit,(value_to_search,))
        StoreUnits = self.mycursor.fetchall()
        return StoreUnits
    

    # Serachs a payment using the the Tenant ID
    def SearchPaymentTenantID(self,TenantId):
        sqlSearchTenant = ("SELECT * FROM PAYMENTS WHERE TenantId LIKE %s")

        value_to_search = f"%{TenantId}%"
        
        self.mycursor.execute(sqlSearchTenant,(value_to_search,))
        tenants = self.mycursor.fetchall()
        return tenants
        




# Operations class that handles CRUDL for Rentals 
class RentalOperations:
    def __init__(self, host, user, password, database) -> None:
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

        self.mycursor = self.mydb.cursor()


    # Helper function that calculates the Duration between Start and End dates
    def CalculateMonthDuration(self,startDate,endDate):
        
        sqlValidate = "SELECT TIMESTAMPDIFF(MONTH, %s, %s)"
        values_to_check = (startDate,endDate)
        self.mycursor.execute(sqlValidate,values_to_check)
        months = self.mycursor.fetchone()[0]
        return months
    
    # Helper function that validates duration of dates
    # Makes sure that transactions are atleast a month apart
    def ValidateDuration(self,startDate,endDate):
        diff = self.CalculateMonthDuration(startDate,endDate)

        start_date_obj = datetime.strptime(startDate, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(endDate, '%Y-%m-%d').date()

        if diff == 0:
            return False

        if start_date_obj.day != end_date_obj.day:
            return False


        if diff != int(diff):
            #raise ValueError('Dates Should atleast be a month/months apart')
            return False
        return True
    
    # Helper function that validates date input 
    def ValidateDate(self,date):
        date_format = r"\d{4}-\d{2}-\d{2}"
        if re.match(date_format,date):
            return True
        else:
            return False

    # Gets all the contents in the Rentals table
    def LoadRentals(self):
        self.mycursor.execute("SELECT * FROM RENTALS")
        rentals = self.mycursor.fetchall()
        
        formatted_rentals = []

        for rental in rentals:
            formated_rentals = []
            for item in rental:
                if isinstance(item,dt.date):
                    formated_rentals.append(item.strftime("%Y-%m-%d"))
                else:
                    formated_rentals.append(item)
            formatted_rentals.append(formated_rentals)
            #print(formated_rentals)

        return formatted_rentals


    # Add a new rental to the rentals table
    def AddRental(self, UnitId, TenantId, StartDate, EndDate):
        try:
            if self.ValidateDate(StartDate) and self.ValidateDate(EndDate):
                if self.ValidateDuration(StartDate, EndDate):
                    sqlAddRental = "INSERT INTO RENTALS(UnitId, TenantId, StartDate, EndDate) VALUES (%s, %s, %s, %s)"
                    value_to_add = (UnitId, TenantId, StartDate, EndDate)
                    self.mycursor.execute(sqlAddRental, value_to_add)
                    self.mydb.commit()
                    return True, ""
                else:
                    raise ValueError("Dates should be at least a month/months apart")
            else:
                raise ValueError("Invalid Date format. Please enter a date in YYYY-MM-DD format")
            
        except ValueError as ve:
            error_message = str(ve)
            print("ValueError caught:", error_message)
            return False, error_message
        
        except mysql.connector.Error as sqle:
            if sqle.errno == errorcode.ER_DUP_ENTRY:
                print("Error: A Tenant can only rent one Unit and vice versa")
                error_message = "Error: A Tenant can only rent one Unit and vice versa"
                return False,error_message
            
            elif sqle.errno == mysql.connector.errorcode.ER_CHECK_CONSTRAINT_VIOLATED:
                print("Error: EndDate must be greater than or equal to StartDate")
                error_message = "Error: EndDate must be greater than or equal to StartDate"
                return False,error_message
            
            else:
                print(f"MySQL Error: {sqle}")
                error_message = f"MySQL Error: {sqle}"
                return False,error_message

        except Exception as e:
            error_message = f"Error adding payments: {e}"
            print(error_message)
            return False, error_message
        
    
    # Deletes selected rental
    def DeleteRental(self,UnitId):
        sqlDeleteRental = "DELETE FROM RENTALS WHERE UnitId = %s"
        value_to_delete = (UnitId,)
        self.mycursor.execute(sqlDeleteRental,value_to_delete)
        self.mydb.commit()
        
    
    # Updates selected rental
    def UpdateRental(self,UnitId,StartDate,EndDate):
        try:
            if self.ValidateDate(StartDate) and self.ValidateDate(EndDate):
                if self.ValidateDuration(StartDate, EndDate):
                    sqlUpdateRental = "UPDATE RENTALS SET StartDate = %s, EndDate = %s WHERE UnitId = %s"
                    value_to_update = (StartDate, EndDate,UnitId)
                    self.mycursor.execute(sqlUpdateRental, value_to_update)
                    self.mydb.commit()
                    return True, ""
                else:
                    raise ValueError("Dates should be at least a month/months apart")
            else:
                raise ValueError("Invalid Date format. Please enter a date in YYYY-MM-DD format")
        
        except ValueError as ve:
            error_message = str(ve)
            print(error_message)
            return False,error_message

        except mysql.connector.Error as sqle:
            if sqle.errno == mysql.connector.errorcode.ER_CHECK_CONSTRAINT_VIOLATED:
                print("Error: EndDate must be greater than or equal to StartDate")
                error_message = "Error: EndDate must be greater than or equal to StartDate"
                return False,error_message
            

        except Exception as e:
            error_message = f"Error adding payments: {e}"
            print(error_message)
            return False, error_message


    # Searches a rental using Store Unit Name
    def SearchRentalUnitName(self,UnitName):

        sqlSearchTenantRental = "SELECT R.UnitId, R.TenantId, R.StartDate,R.EndDate FROM RENTALS R INNER JOIN STOREUNITS S ON R.UnitId = S.UnitId WHERE S.UnitName LIKE %s"
        value_to_search = f"%{UnitName}%"
        self.mycursor.execute(sqlSearchTenantRental,(value_to_search,))
        
        TenantRental = self.mycursor.fetchall()

        formatted_rentals = []

        for rental in TenantRental:
            formated_rentals = []
            for item in rental:
                if isinstance(item,dt.date):
                    formated_rentals.append(item.strftime("%Y-%m-%d"))
                else:
                    formated_rentals.append(item)
            formatted_rentals.append(formated_rentals)
            
            #print(formated_payments)
        return formatted_rentals
    
    # Searches a rental using Tenant Name
    def SearchRentalTenantName(self,TenantName):

        sqlSearchTenantRental = "SELECT R.UnitId, R.TenantId, R.StartDate,R.EndDate FROM RENTALS R INNER JOIN TENANTS T ON R.TenantId = T.TenantId WHERE T.TenantName LIKE %s"
        value_to_search = f"%{TenantName}%"
        self.mycursor.execute(sqlSearchTenantRental,(value_to_search,))
        
        TenantRental = self.mycursor.fetchall()

        formatted_rentals = []

        for rental in TenantRental:
            formated_rentals = []
            for item in rental:
                if isinstance(item,dt.date):
                    formated_rentals.append(item.strftime("%Y-%m-%d"))
                else:
                    formated_rentals.append(item)
            formatted_rentals.append(formated_rentals)

            #print(formated_payments)
        return formatted_rentals

    
    # Searches a rental using Store Unit ID
    def SearchRentalUnitID(self,UnitId):
        sqlSearchUnit = ("SELECT * FROM RENTALS WHERE UnitId LIKE %s")

        value_to_search = f"%{UnitId}%"
        
        self.mycursor.execute(sqlSearchUnit,(value_to_search,))

        StoreUnits = self.mycursor.fetchall()
        #return StoreUnits

        formatted_rentals = []
        for rental in StoreUnits:
            formated_rentals = []
            for item in rental:
                if isinstance(item,dt.date):
                    formated_rentals.append(item.strftime("%Y-%m-%d"))
                else:
                    formated_rentals.append(item)
            formatted_rentals.append(formated_rentals)

            #print(formated_payments)
        return formatted_rentals
    

    # Searches a rental using Tenant ID
    def SearchRentalTenantID(self,TenantId):
        sqlSearchTenant = ("SELECT * FROM RENTALS WHERE TenantId LIKE %s")

        value_to_search = f"%{TenantId}%"
        
        self.mycursor.execute(sqlSearchTenant,(value_to_search,))
        tenants = self.mycursor.fetchall()
        #return tenants
        #return StoreUnits

        formatted_rentals = []
        for rental in tenants:
            formated_rentals = []
            for item in rental:
                if isinstance(item,dt.date):
                    formated_rentals.append(item.strftime("%Y-%m-%d"))
                else:
                    formated_rentals.append(item)
            formatted_rentals.append(formated_rentals)

            #print(formated_payments)
        return formatted_rentals 

     


#operations = TenantOperations("localhost", "root", "2022-1729", "STORE_DATABASE")
#operations.LoadTenants()

#operations.UpdateTenant('1234-3294','Klien Dalin', 'iangabriel@gmail.com', '09666283660', '2022-0000')

#operations.AddTenant('1234-5353', 'Sacrificial Lamb', 'ZUCKER@example.com', '09263456456')

#operations.AddTenant('2022-0000','Klien Dalin', 'iangabriel@gmail.com', '09666283660')

#operations.DeleteTenant("1234-3294")

#operations.SearchTenant("1234")

#Unit_operations = StoreUnitOperations("localhost", "root", "2022-1729", "STORE_DATABASE")
#Unit_operations.LoadStoreUnits()


#Unit_operations.UpdateStoreUnit('ABC-0000', 'Diwata Pares Overload Iligan', 'Food Vendor','200000','ABC-0000')

#Unit_operations.AddStoreUnit('ABC-0000', 'Diwata Pares Overload', 'Food Vendor','Vacant','200,000')

#Unit_operations.DeleteStoreUnit("ABC-0000")

#Unit_operations.SearchStoreUnit("abc")


#PaymentOps = PaymentOperations("localhost", "root", "2022-1729", "STORE_DATABASE")
#PaymentOps.LoadPayments()

#PaymentOps.AddPayment("ABC-0000","2022-0000","2024-05-12","G-Cash","Paid")

#PaymentOps.DeletePayment("ABC-0000")

#PaymentOps.UpdatePayment("ABC-0000","2024-05-13","Credit Card","Paid")

#PaymentOps.SearchTenantPayment("")




#RentalOps = RentalOperations("localhost", "root", "2022-1729", "STORE_DATABASE")
#RentalOps.LoadRentals()

#RentalOps.AddRental("ABC-7070","2326-5453","2024-02-13","2024-04-13")

#RentalOps.DeleteRental("ABC-0000")

#RentalOps.UpdateRental("ABC-0000","2024-05-13","2024-07-13",)

#RentalOps.SearchTenantRental("k")