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

create_table = "CREATE TABLE t1 (id VARCHAR(36), datetime DATETIME(0), weight DECIMAL(2,2));"
drop_table = "DROP TABLE IF EXISTS t1;"
select = "SELECT * FROM t1;"
show = "SHOW DATABASES;" # should return 'psupresc_dropbox'
show_tables = "SHOW TABLES;"
commit = "COMMIT;"

# Simple routine to run a query on a database and print the results:
def doQuery( conn ) :
    cur = conn.cursor()

    # for i in range(0, 5):
    #     insert = "INSERT INTO t1(id, datetime, weight) VALUES ('%s', '%s', '%1.2f');" % ("dropboxtest1", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), float(decimal.Decimal(random.randrange(155, 389))/400))
    #     cur.execute( insert )
        
    # cur.execute( commit )
    cur.execute( select )

    print("–––––––––––––––––––––––––––––––––")
    print("|","id","|","datetime","|","weight","|")
    print("–––––––––––––––––––––––––––––––––")
    for x in cur.fetchall():
        print("|",x[0],"|",x[1],"|",x[2],"|")
    print("–––––––––––––––––––––––––––––––––")

print( "Using pymysql:" )
import pymysql
myConnection = pymysql.connect( host=hostname, user=username, passwd=password, db=database )
doQuery( myConnection )
myConnection.close()