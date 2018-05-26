'''
Created on 10-Mar-2018

@author: Dishant
'''
import cx_Oracle

con = cx_Oracle.connect('system/2314022@Localhost/XE')
cur= con.cursor()