'''
Created on 14-Jan-2018

@author: Dishant
'''

import menus
from datetime import datetime
from datetime import date
from terminaltables import AsciiTable
from easygui import passwordbox
from passlib.hash import sha256_crypt
import oracleconnection
import generalfunc

generalfunc.foo()
today= date.today()
print(today)
print("")
while True:
    menus.mainmenu()
oracleconnection.con.close()
