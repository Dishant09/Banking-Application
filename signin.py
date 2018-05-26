'''
Created on 09-Mar-2018

@author: Dishant
'''
import oracleconnection
from easygui import passwordbox
import menus

def signin():
    x=0
    while x<3:
        acc=input("Please enter your Account Number:")
        passwrd=passwordbox("Please enter the Password:")
        oracleconnection.cur.execute('SELECT * from DISHANT.CUSTOMER WHERE ACCNO=:1 and password=:2',(acc,passwrd))
        row=oracleconnection.cur.fetchall()
        oracleconnection.con.commit()
        if row:
            for r in row:
                menus.submenu(r[0],acc,passwrd)
        else:
            print("Invalid USER-ID or Password!")
            x=x+1
    if x==3 :
        oracleconnection.cur.execute("""DELETE DISHANT.CUSTOMER WHERE accno=:1""",(acc,))
        oracleconnection.con.commit()
        print("More than 3 attempts are not allowed")
        menus.mainmenu()
        
def adminsignin():
    x=0
    while x<3:
        print("\n***************************************************************************")
        admin=input("Admin ID:")
        passwrd=passwordbox("Password:")
        oracleconnection.cur.execute('SELECT * from DISHANT.ADMIN WHERE id=:1 and password=:2',(admin,passwrd))
        r=oracleconnection.cur.fetchall()
        oracleconnection.con.commit()
        if r:
            menus.submenu2(admin,passwrd)
        else:
            print("Invalid USER-ID or Password!")
            x=x+1
    if x==3:
        print("More than 3 attempts are not allowed")
        menus.mainmenu()

