'''
Created on 09-Mar-2018

@author: Dishant
'''
from datetime import datetime
from terminaltables import AsciiTable
import signup
import signin
import corefunctionalities
import generalfunc
import oracleconnection
from datetime import date

def mainmenu():
    print("**********************************MAIN MENU********************************\n\n1. Sign Up (New Customer)\n2. Sign In (Existing Customer)\n3. Admin Sign In\n4. Exit\n")
    print("***************************************************************************")
    mainmenu=input("Enter Choice:")
    if mainmenu=='1':
        signup.signup()
    elif mainmenu=='2':
        signin.signin()
    elif mainmenu=='3':
        signin.adminsignin()
    elif mainmenu=='4':
        print("\nThank you for choosing our service...")
        exit()
    else:
        print("\nPlease enter a valid option")

def submenu(cid,acc,p):
    print("\n**********************************SUB MENU**********************************\n 1. View and Edit Details \n 2. Money Deposit \n 3. Money Withdrawal \n 4. Print Statement \n 5. Transfer Money \n 6. Fixed Deposit \n 7. Account Closure \n 8. Customer Logout\n***************************************************************************")
    choice=int(input("Enter Choice:"))
    
    if choice==1:
        corefunctionalities.personaldetails(cid,acc,p)
        
    elif choice==2:
        print("\n*****************Deposit*****************\n")
        oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        print("Opening Balance=",row[0][0])
        amount=int(input("Enter the amount to be deposited:"))
        verify=generalfunc.verifypassword(acc)
        if verify:
            row=generalfunc.otp(acc)
            print(row)
            if row:
                corefunctionalities.deposit(cid,acc,amount)
            else:
                print("Invalid OTP")
        else:
            print("\nWrong password....Please try again")
        submenu(cid,acc,p)
        
    elif choice==3:
        print("\n*****************Withdrawal*****************\n")
        oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        print("Opening Balance=",row[0][0])
        amount=int(input("Enter the amount that you wish to withdraw:"))
        verify=generalfunc.verifypassword(acc)
        if verify:
            corefunctionalities.withdrawal(cid,acc,amount)
        else:
            print("\nWrong password....Please try again")
        submenu(cid,acc,p)
        
    elif choice==4:
        print("\n*****************Print Statement*****************\n")
        print("1. All Transactions \n2. For Specific Dates \n3. Annual Statements\n")
        typeofstatement=input("Enter Choice:")
        if typeofstatement=="1":
            oracleconnection.cur.execute("SELECT * FROM DISHANT.RECORD WHERE CID=:1 ",(cid,))
            oracleconnection.con.commit()
            print("")
            table_data = [['Transaction ID','Customer ID', 'Account No.', 'Date of Transaction', 'Description','Amount', 'Total Balance']]
            row=oracleconnection.cur.fetchall()
            if row:
                for val in row:
                    table_data.append(val)
                    table = AsciiTable(table_data, "Transactions/Statements")
                print(table.table) 
            else:
                print("\nNo Record Found")
            submenu(cid,acc,p)
            
        elif typeofstatement=="2":
            datef=input("Date From(MM/DD/YYYY):")
            datet=input("Date To(MM/DD/YYYY):")
            today= datetime.today()
            datef=datetime.strptime(datef, '%m/%d/%Y')
            datet=datetime.strptime(datet, '%m/%d/%Y')
            if(datet<=today):
                corefunctionalities.printstatement(acc,datef,datet)
            else:
                print("You are using future date...Please enter valid date")
            submenu(cid,acc,p)
            
        elif typeofstatement=="3":
            year=input("\nEnter the year")
            datef="01/01/%s" %year
            datet="12/31/%s" %year
            datef=datetime.strptime(datef, '%m/%d/%Y')
            datet=datetime.strptime(datet, '%m/%d/%Y')
            corefunctionalities.printstatement(acc,datef,datet)
            submenu(cid,acc,p)
        else:
            print("\nChoose correct option")
            submenu(cid,acc,p)
            
    elif choice==5:
        print("\n*****************Transfer Money*****************\n")
        oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        print("Opening Balance=",row[0][0])
        acc2=input("Enter account no. to transfer money: ")
        oracleconnection.cur.execute('SELECT ACCNO FROM DISHANT.CUSTOMER WHERE accno=:1',(acc2,))
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        if row:
            amount=int(input("Enter the amount to transfer:"))
            verify=generalfunc.verifypassword(acc)
            if verify:
                corefunctionalities.transfer(cid,acc,acc2,amount)
            else:
                print("\nWrong password....Please try again")    
        else:
            print("\nNo such account found")
        submenu(cid,acc,p)
    
    elif choice==6:
        print("\n*****************Fixed Deposit*****************\n")
        corefunctionalities.fixeddeposit(cid,acc,p)
        submenu(cid,acc,p)
        
    elif choice==7:
        print("\n*****************Account Close*****************\n")
        choice=input("Press 1 to confirm or press another key to return to previous menu")
        if choice=="1":
            verify=generalfunc.verifypassword(acc)
            if verify: 
                corefunctionalities.accountclose(acc,p)
                print("Your account is closed")
                mainmenu()
            else:
                print("\nWrong password....Please try again") 
                submenu(cid,acc,p)
        else: 
            submenu(cid,acc,p)
            
    elif choice==8:
        mainmenu()
    else:
        print("\nChoose correct option")
        submenu(cid,acc,p)
    
def submenu2(admin,passwrd):
    print("\n1.Print closed account history")
    print("2.Print all transactions")
    print("3.View List of FD's")
    print("4.View List of Customers")
    print("5.Admin logout\n")
    choice=int(input("Enter choice:"))
    print("")
    if choice==1:
        oracleconnection.cur.execute("SELECT * FROM DISHANT.HISTORY ORDER BY CLOSING_DATE DESC")
        oracleconnection.con.commit()
        table_data = [['Customer ID', 'Account No.','Name','Balance', 'Closing Date', 'Address','Contact Number']]
        row=oracleconnection.cur.fetchall()
        if row:
            for val in row:
                table_data.append(val)
                table = AsciiTable(table_data, "Closed Accounts")
            print(table.table) 
            submenu2(admin,passwrd)
        else:
            print("History not found")
            submenu2(admin,passwrd)
            
    elif choice==2:   
        datef=input("Date From(MM/DD/YYYY):")
        datet=input("Date To(MM/DD/YYYY):")
        today= datetime.today()
        datef=datetime.strptime(datef, '%m/%d/%Y')
        datet=datetime.strptime(datet, '%m/%d/%Y')
        if(datet<=today):
            if datef>datet :
                print("\nInvalid date")
            else:
                oracleconnection.cur.execute('SELECT * FROM DISHANT.RECORD WHERE (dateoftransaction>=:1 AND dateoftransaction<=:2) ORDER BY dateoftransaction DESC',(datef,datet))
                oracleconnection.con.commit()
                print("")
                table_data = [['Transaction ID','Customer ID', 'Account No.', 'Date of Transaction', 'Description','Amount', 'Total Balance']]
                row=oracleconnection.cur.fetchall()
                if row:
                    for val in row:
                        table_data.append(val)
                        table = AsciiTable(table_data, "Transactions/Statements")
                        print(table.table) 
                else:
                    print("\nNo Record Found") 
            submenu2(admin,passwrd)
           
        else:
            print("You are using future date...Please enter valid date")  
            submenu2(admin,passwrd)
    
    
    elif choice==3:
        oracleconnection.cur.execute("SELECT * FROM DISHANT.TEMPFD ORDER BY TRANSACTIONID")
        oracleconnection.con.commit()
        table_data = [['Customer ID', 'Account No.','Amount','Tenure', 'Interest', 'Opening Date','Last Date','Transaction ID']] 
        row=oracleconnection.cur.fetchall()
        if row:
            for val in row:
                table_data.append(val)
                table = AsciiTable(table_data, "Fixed Deposits")
            print(table.table) 
            submenu2(admin,passwrd)
        else:
            print("Record not found")
            submenu2(admin,passwrd)
            
    elif choice==4:
        oracleconnection.cur.execute("SELECT CID,ACCNO,NAME,ADDRESS,ACCTYPE,BALANCE,OPENINGDATE,CONTACT_NUMBER,AADHAARNUMBER FROM DISHANT.CUSTOMER ORDER BY CID")
        oracleconnection.con.commit()
        
        table_data = [['Customer ID', 'Account No.','Name','Address', 'Account Type', 'Balance','Opening Date','Contact Number','Aadhaar Number']] 
        row=oracleconnection.cur.fetchall()
        if row:
            for val in row:
                table_data.append(val)
                table = AsciiTable(table_data, "Customer Details")
            print(table.table) 
            submenu2(admin,passwrd)
        else:
            print("Record not found")
            submenu2(admin,passwrd)    
                      
    elif choice==5:
        mainmenu()
        
    else:
        print("Invalid choice")
        submenu2(admin,passwrd)
        
        