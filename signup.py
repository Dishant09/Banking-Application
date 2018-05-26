'''
Created on 09-Mar-2018

@author: Dishant
'''
import generalfunc
import menus
import oracleconnection
from datetime import date

def signup():
    print("\nEnter the following details:")
    fname=input("First Name:")
    lname=input("Last Name:")
    name="%s %s" %(fname,lname)
    print("Address:")
    add1=input("Line1(House No.):")
    add2=input("Line2(Street/Colony/Road):")
    add3=input("City:")
    add4=input("State:")
    add5=generalfunc.pincode()
    address="%s %s,%s,%s,%d" %(add1,add2,add3,add4,add5)
    acctype=generalfunc.account()
    contact_no=input("Contact No.:")
    aadhaar_number=generalfunc.aadhaarnumber()
    passwrd=generalfunc.password()
    bal=generalfunc.balance(acctype)
    today= date.today()
    
    oracleconnection.cur.execute("""SELECT AADHAARNUMBER FROM DISHANT.CUSTOMER WHERE AADHAARNUMBER=:1""",(aadhaar_number,))
    oracleconnection.con.commit()
    row= oracleconnection.cur.fetchall()
    count=oracleconnection.cur.rowcount
    
    if count==0:
        oracleconnection.cur.execute('SELECT DISHANT.CID.NEXTVAL FROM DUAL')
        oracleconnection.con.commit()
        row= oracleconnection.cur.fetchall()
        for r in row:
            cid="%d" %(r[0])
    else:
        oracleconnection.cur.execute('SELECT CID FROM DISHANT.CUSTOMER WHERE AADHAARNUMBER=:1',(aadhaar_number,))
        oracleconnection.con.commit()
        row= oracleconnection.cur.fetchall()
        cid= row[0][0]
    
    oracleconnection.cur.execute('SELECT DISHANT.ACCNO.NEXTVAL FROM DUAL')
    oracleconnection.con.commit()
    row= oracleconnection.cur.fetchall()
    for r in row:
        accno="%s%d" %('ACN',r[0])

    oracleconnection.cur.execute('INSERT INTO DISHANT.CUSTOMER VALUES(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)',(cid,accno,name,address,acctype,bal,passwrd,today,contact_no,aadhaar_number))
    oracleconnection.con.commit()
    print("***************************************************************************")
    print("New Customer ID created\n")
    print("Customer ID:",cid)
    print("Account No.",accno)
    print("***************************************************************************")
    menus.mainmenu()