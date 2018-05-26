'''
Created on 09-Mar-2018

@author: Dishant
'''
from easygui import passwordbox
import oracleconnection
import time, threading
from datetime import date,timedelta,datetime
import pyotp
from twilio.rest import Client
from flask import request

def pincode():
    add5=int(request.form['add5'])
    if add5 >= 100000 and add5 <= 999999:
        return add5
    else:
        print("Enter 6 digit number:")
        return pincode()

def aadhaarnumber():
    aadhaar_number=int(request.form['aadhaar_number'])
    if  aadhaar_number >= 100000000000 and aadhaar_number <= 999999999999:
        return aadhaar_number
    else:
        print("Enter 12 digit aadhaar number:")
        return aadhaarnumber()

def account():
    acctype=request.form['acctype']
    if acctype!="SA" and acctype!="CA":
        print("Invalid entry")
        return account()
    else:
        return acctype

def password():
    passwrd=request.form['passwrd']
    i=len(passwrd)
    if(i>=8):
        passwrd2=request.form['passwrd2']
        if(passwrd==passwrd2):
            return passwrd
        else:
            print("Password does not match")
            return password()
    else:
        print("Invalid password (Too Short)")
        return password()

def verifypassword(acc):
    passwrd=passwordbox("Please enter your password:")
    oracleconnection.cur.execute("""SELECT PASSWORD FROM DISHANT.CUSTOMER WHERE ACCNO=:1""",(acc,))
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    if(passwrd==row[0][0]):
        return True
    else: 
        return False
     
def balance(acctype):
    if acctype=="CA":
        bal=5000
    else:
        bal=0
    return bal

def checkbalance(accno):
    oracleconnection.cur.execute("SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO=:1",(accno,))
    row=oracleconnection.cur.fetchall()
    balance=row[0][0]
    print("\nYour current balance:",balance)
    
def foo():
    oracleconnection.cur.execute("""SELECT ACCNO,AMOUNT,TENURE,INTEREST,OPENINGDATE,LASTDATE,TRANSACTIONID,CID FROM DISHANT.FD""")
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    count=oracleconnection.cur.rowcount
   
    if row:
        i=0
        while i<count:
            acc=row[i][0]
            amount=row[i][1]
            tenure=row[i][2]
            interest=row[i][3]
            ldate=row[i][5]
            tid=row[i][6]
            today=datetime.now()
            cid=row[i][7]
            if today>ldate:
                simpleinterest=(amount*interest*tenure)/100
                amount=amount+simpleinterest
                oracleconnection.cur.execute("""UPDATE DISHANT.CUSTOMER SET BALANCE=BALANCE+:1 WHERE ACCNO=:2""",(amount,acc))
                description="%s %d" %('Deposit from FD',amount)
                oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
                oracleconnection.con.commit()
                row= oracleconnection.cur.fetchall()
                newtid=row[0][0]
                oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
                row=oracleconnection.cur.fetchall()
                balance=row[0][0]
                oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES (:1,:2,:3,:4,:5,:6,:7)',(newtid,cid,acc,today,description,amount,balance))
                oracleconnection.con.commit()
                oracleconnection.cur.execute("""DELETE FROM DISHANT.FD WHERE TRANSACTIONID=:1""",(tid,))
                oracleconnection.con.commit()  
            else:
                pass
            i=i+1    
    
    threading.Timer(86400, foo).start()
    
def fd(cid,acc,amount,interest,tenure,lastdate,p):
    today= date.today()
    description="%s %d" %('Fixed Deposit of',amount)
    oracleconnection.cur.execute('SELECT BALANCE,ACCTYPE FROM DISHANT.CUSTOMER WHERE ACCNO=:1 and balance>=:2',(acc,amount))
    oracleconnection.con.commit()
    row=oracleconnection.cur.fetchall()
    if row:
        for r in row:
            typeacc=r[1]
            am=r[0]-amount
        if (typeacc=="CA" and am>=5000) or typeacc=='SA':
            oracleconnection.cur.execute("""UPDATE DISHANT.CUSTOMER SET balance=balance-:1 where ACCNO=:2 and balance>:1""" ,(amount,acc))
            oracleconnection.con.commit()
            oracleconnection.cur.execute('SELECT DISHANT.TRANSACTIONID.NEXTVAL FROM DUAL')
            row= oracleconnection.cur.fetchall()
            tid=row[0][0]
            oracleconnection.cur.execute('INSERT INTO DISHANT.RECORD VALUES(:1,:2,:3,:4,:5,:6,:7)',(tid,cid,acc,today,description,amount,am))
            oracleconnection.cur.execute('INSERT INTO DISHANT.FD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)',(cid,acc,amount,tenure,interest,today,lastdate,tid))
            oracleconnection.cur.execute("""INSERT INTO DISHANT.TEMPFD VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""",(cid,acc,amount,tenure,interest,today,lastdate,tid))
            oracleconnection.cur.execute("""SELECT BALANCE FROM DISHANT.CUSTOMER WHERE ACCNO= :param1""",{'param1':acc})
            row=oracleconnection.cur.fetchall()
            print("Transaction ID:",tid)
            print("Closing balance:",row[0][0])
            oracleconnection.con.commit()
        else:
            print("Min balance is not sufficient")
    else:
        print("Insufficient amount...Transaction failed") 
 
def sendmsg(contact_number,otp):

    account_sid = "account id"
    auth_token = "token"
    client = Client(account_sid, auth_token)
    
    contact_number="+91%s" %contact_number
    print(contact_number)
    client.messages.create(
        "contact number ",
        body=otp,
        from_="+1 813-750-0171 ",
        )
    
def otp(accno):  
    totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")
    otp=totp.now()
    oracleconnection.cur.execute("""SELECT CONTACT_NUMBER FROM DISHANT.CUSTOMER WHERE ACCNO=:1""",(accno,))
    contact_number=oracleconnection.cur.fetchall()
    contact_number=contact_number[0][0]
    sendmsg(contact_number,otp)
    a=input("Enter the otp")   
    print(a)
    b=totp.verify(a)
    print(b) 
    return b
    
