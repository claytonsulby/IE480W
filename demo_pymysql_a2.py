#!/usr/bin/python

from __future__ import print_function
from datetime import datetime
import random
import decimal
import time

hostname = '70.32.23.81'
username = 'psupresc_admin'
password = 'nipdy1-zagpos-nuHxoz'
database = 'psupresc_dropbox'

create_table = "CREATE TABLE t1 (date DATETIME(0), time TIME(0), weight DECIMAL(2,2));"
select = "SELECT * FROM t1;"
show = "SHOW DATABASES;" # should return 'psupresc_dropbox'
show_tables = "SHOW TABLES;"
commit = "COMMIT;"

# Simple routine to run a query on a database and print the results:
def doQuery( conn ) :
    cur = conn.cursor()

    for i in range(0, 20):
        insert = "INSERT INTO t1(date, time, weight) VALUES ('%s', '%s', '%1.2f');" % (datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%H:%M:%S"), float(decimal.Decimal(random.randrange(155, 389))/400))
        time.sleep(2.4)
        cur.execute( insert )
        
    cur.execute( commit )
    cur.execute( select )

    print("–––––––––––––––––––––––––––––––––")
    print("|","date","|","time","|","weight","|")
    print("–––––––––––––––––––––––––––––––––")
    for x in cur.fetchall():
        print("|",x[0],"|",x[1],"|",x[2],"|")
    print("–––––––––––––––––––––––––––––––––")

# print( "Using mysqlclient (MySQLdb):" )
# import MySQLdb
# myConnection = MySQLdb.connect( host=hostname, user=username, passwd=password, db=database )
# doQuery( myConnection )
# myConnection.close()

# print( "Using mysql.connector:" )
# import mysql.connector
# myConnection = mysql.connector.connect( host=hostname, user=username, passwd=password, db=database )
# doQuery( myConnection )
# myConnection.close()

print( "Using pymysql:" )
import pymysql
myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database )
doQuery( myConnection )
myConnection.close()