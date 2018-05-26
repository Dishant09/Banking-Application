'''
Created on 09-Mar-2018

@author: Dishant
'''
import datetime
from datetime import date
from terminaltables import AsciiTable
import oracleconnection
import generalfunc
import menus

def personaldetails(cid,acc,p):
    print("\n**********************VIEW AND EDIT PERSONAL DETAILS*********************\n 1. View Personal Details \n 2. Check Balance \n 3. Change Address \n 4. Change Password \n 5. Change Contact Number \n 6. Previous Menu \n***************************************************************************")
    choice=input("\nEnter Choice")
    
    if choice=="1":
        print("")
        table_data = [['Customer ID', 'Account No.', 'Name', 'Address','Account Type', 'Balance','Opening Date', 'Contact Number']]
        oracleconnection.cur.execute("""SELECT CID,ACCNO,NAME,ADDRESS,ACCTYPE,BALANCE,OPENINGDATE,CONTACT_NUMBER FROM DISHANT.CUSTOMER WHERE ACCNO=:1""",(acc,))
        row=oracleconnection.cur.fetchall()
        if row:
            for val in row:
                table_data.append(val)
                table = AsciiTable(table_data, "Personal Details")
            print(table.table) 
        else:
            print("\nNo Record Found")
            
        personaldetails(cid,acc,p)
            
    elif choice=="2":
        generalfunc.checkbalance(acc)
        personaldetails(cid,acc,p)
        
    elif choice=="3": 
        print("\n*****************Change Address*****************")
        oracleconnection.cur.execute("""SELECT ADDRESS FROM DISHANT.CUSTOMER WHERE ACCNO=:1""",(acc,))
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        print("\nCurrent Address:",row[0][0])
        print("")
        choice=int(input("Press 1 to continue...or press any other key to return to previous menu\n"))
        if choice==1:
            add1=input("Line1(House No.):")
            add2=input("Line2(Street/Colony/Road):")
            add3=input("City:")
            add4=input("State:")
            add5=generalfunc.pincode()
            address="%s %s,%s,%s,%d" %(add1,add2,add3,add4,add5)
            oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER set address=:1 where ACCNO=:2',(address,acc))
            oracleconnection.con.commit()
            print("\nAddress is changed")
            print("New address:",address)
            personaldetails(cid,acc,p)
        else:
            personaldetails(cid,acc,p)

    elif choice=="4":
        print("\n*****************Change Password*****************")
        verified=generalfunc.verifypassword(acc)
        if verified==True:
            print("")
            choice=int(input("Press 1 to continue...or press any other key to return to previous menu\n"))
            if choice==1:
                passwrd=generalfunc.password()
                oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET PASSWORD =:1 where ACCNO=:2',(passwrd,acc))
                oracleconnection.con.commit()
                print("\nPassword is changed")
                
            else:
                personaldetails(cid,acc,p)
        else:
            print("Password does not match...Please try again")
        personaldetails(cid,acc,p)    
        
    elif choice=="5":
        print("\n*****************Change Contact Number*****************")
        oracleconnection.cur.execute("""SELECT CONTACT_NUMBER FROM DISHANT.CUSTOMER WHERE ACCNO=:1""",(acc,))
        oracleconnection.con.commit()
        row=oracleconnection.cur.fetchall()
        print("\nCurrent Contact Number:",row[0][0])
        print("")
        choice=int(input("Press 1 to continue...or press any other key to return to previous menu\n"))
        if choice==1:
            contact_no=input("Contact No.:")
            oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET CONTACT_NUMBER =:1 where ACCNO=:2',(contact_no,acc))
            oracleconnection.con.commit()
            print("\nContact is changed")

            personaldetails(cid,acc,p)
        else:
            personaldetails(cid,acc,p)
    
    elif choice=="6":
        menus.submenu(cid, acc, p)
    else:
        print("\nChoose correct option")
        personaldetails(cid,acc,p)

def deposit(cid,acc,amount):  
    today= date.today()
    description="%s %d" %('Deposit',amount)
    oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET balance=balance+:1 where accno=:2' ,(amount,acc))
    oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
    oracleconnection.con.commit()
    row= oracleconnection.cur.fetchall()
    tid=row[0][0]
    oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
    row=oracleconnection.cur.fetchall()
    balance=row[0][0]
    oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES (:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,balance))
    oracleconnection.con.commit()
    print("\nDeposit successful")
    print("Transaction ID:",tid)
    print("Closing Balance=",row[0][0])
      
def withdrawal(cid,acc,amount):
    today= date.today()
    description="%s %d" %('Withdrawal',amount)
    oracleconnection.cur.execute('SELECT balance,acctype FROM DISHANT.CUSTOMER WHERE accno=:1 and balance>= :2',(acc,amount))
    row=oracleconnection.cur.fetchall()
    if row:
        for r in row:
            typeacc=r[1]
            am=r[0]-amount
        if (typeacc=='CA' and am>=5000) or typeacc=='SA':
            oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET balance=balance-:1 where accno=:2 and balance>:1' ,(amount,acc))
            oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
            oracleconnection.con.commit()
            row= oracleconnection.cur.fetchall()
            tid=row[0][0]
            oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,am))
            oracleconnection.con.commit()
            print("\nWithdrawal successful")
            oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
            row=oracleconnection.cur.fetchall()
            print("Closing Balance=",row[0][0])
            print("Transaction ID:",tid)
        else:
            print("\nTransaction cannot be completed as you are not able to maintain min balance or insufficient amount..Try withdrawing less amount")
    else:
        print("\nInsufficient amount..")

def transfer(cid,acc,acc2,amount):
    today= date.today()
    description="%s %d %s %s" %('Tranfer',amount,'to',acc2)
    oracleconnection.cur.execute('SELECT balance,acctype FROM DISHANT.CUSTOMER WHERE accno=:1 and balance>=:2',(acc,amount))
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    if row:
        for r in row:
            typeacc=r[1]
            am=r[0]-amount
        if (typeacc=='CA' and am>=5000) or typeacc=='SA':
            oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET balance=balance-:1 where accno=:2 and balance>:1' ,(amount,acc))
            oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
            row= oracleconnection.cur.fetchall()
            tid=row[0][0]
            oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,am))
            oracleconnection.cur.execute("""SELECT BALANCE,CID FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc2})
            row=oracleconnection.cur.fetchall()
            cid1=row[0][1]
            a="%s %d %s %s" %('Deposit',amount,'by',acc)
            oracleconnection.cur.execute('UPDATE DISHANT.CUSTOMER SET balance=balance+:1 where accno=:2' ,(amount,acc2))
            oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc2})
            row=oracleconnection.cur.fetchall()
            balance=row[0][0]
            oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid1,acc2,today,a,amount,balance))
            oracleconnection.con.commit()
            print("Transfer successful")
            oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
            row=oracleconnection.cur.fetchall()
            print("Closing balance:",row[0][0])
            print("Transaction ID:",tid)
            oracleconnection.con.commit()
        else:
            print("Min balance is not sufficient")
    else:
        print("Insufficient amount...Transaction failed")
        
def printstatement(acc,datefrom,dateto):

    if datefrom>dateto :
        print("\nInvalid date")
    else:
        oracleconnection.cur.execute('SELECT * FROM DISHANT.RECORD WHERE accno=:1 AND (dateoftransaction>=:2 AND dateoftransaction<=:3) ORDER BY dateoftransaction DESC',(acc,datefrom,dateto))
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
 
def fixeddeposit(cid,acc,p):
    
    oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    print("Opening Balance=",row[0][0])
    print("\n*****************Enter the tenure****************\n 1. 6 Months(at 4%) \n 2. 1 year(at 4%) \n 3. 7 years(at 5.75%)  \n 4. 10 years(at 6%) \n*************************************************")
    choice=input("\nEnter choice:")
    amount=int(input("\nEnter the amount for fixed deposit"))
    
    if choice=='1':
        interest=4
        tenure=0.5
        lastdate=datetime.date.today() + datetime.timedelta(6*365/12)
        generalfunc.fd(cid,acc,amount,interest,tenure,lastdate,p)
        
    elif choice=="2":
        interest=4
        tenure=1    
        lastdate=datetime.date.today() + datetime.timedelta(365)
        generalfunc.fd(cid,acc,amount,interest,tenure,lastdate,p)
    
    elif choice=="3":
        interest=5.75
        tenure=7
        lastdate=datetime.date.today() + datetime.timedelta(7*365)
        generalfunc.fd(cid,acc,amount,interest,tenure,lastdate,p)
    
    elif choice=="4":
        interest=6
        tenure=10
        lastdate=datetime.date.today() + datetime.timedelta(10*365)
        generalfunc.fd(cid,acc,amount,interest,tenure,lastdate,p)
    
    else:
        print("Enter valid option")  
               
def accountclose(acc,p):
    today= date.today()
    oracleconnection.cur.execute('SELECT cid,accno,name,balance,address,CONTACT_NUMBER FROM DISHANT.CUSTOMER WHERE accno=:1 AND password=:2',(acc,p))
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    for r in row:
        oracleconnection.cur.execute('insert into DISHANT.history values(:1,:2,:3,:4,:5,:6,:7)',(r[0],r[1],r[2],r[3],today,r[4],r[5]))
        oracleconnection.con.commit()
        break
    oracleconnection.cur.execute('DELETE DISHANT.CUSTOMER WHERE accno=:1 and password=:2',(acc,p))
    oracleconnection.con.commit()
    msg="%s %s %s" %(r[3],'amount is send to',r[4])
    print("")
    print(msg)
    
