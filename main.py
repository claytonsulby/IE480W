#! /usr/bin/python3

import time
import sys
from datetime import datetime

import pymysql

from smtp import *
from log import *

import RPi.GPIO as GPIO
from hx711 import HX711

DEBUG = False
TWOCHANNEL = False



referenceUnit = 387.018518

def wait_for_connection( hostname, username, password, database ):
    while True:
        try:
            response = pymysql.connect( host=hostname, user=username, passwd=password, db=database )
            return response
        except OSError:
            log("ERROR", "could not connect to database. Retrying...")


def cleanAndExit():
    log("DEBUG", "Cleaning...")

    GPIO.cleanup()
        
    log("DEBUG", "Bye!")
    sys.exit()



def main():
    hx = HX711(5, 6)

    # I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
    # Still need to figure out why does it change.
    # If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
    # There is some code below to debug and log the order of the bits and the bytes.
    # The first parameter is the order in which the bytes are used to build the "long" value.
    # The second paramter is the order of the bits inside each byte.
    # According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
    hx.set_reading_format("MSB", "MSB")

    # HOW TO CALCULATE THE REFFERENCE UNIT
    # To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
    # In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
    # and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
    # If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.


    #used refrence weight of a bottle (2.25 lbs = 1020.56 grams)
    #displayed weight was 104675.111
    #following rule of thirds, 104675.111 / 1020.56 = 102.56

    hx.set_reference_unit(referenceUnit)

    hx.reset()

    if TWOCHANNEL:
        # to use both channels, you'll need to tare them both
        hx.tare_A()
        hx.tare_B()
    else:
        hx.tare()

    log("DEBUG", "Tare done! Add weight now...")





    ##############################################################################################
    #at end of example.py, move log.csv to different folder for officer meyer ease of use
    #use new location to email to her 
    ##############################################################################################

    hostname = '70.32.23.81'
    username = 'psupresc_admin'
    password = 'nipdy1-zagpos-nuHxoz'
    database = 'psupresc_dropbox'

    log("DEBUG", "Initializing Connection to host:%s db:%s user:%s" % (hostname, database, username))
    
    log("DEBUG", "Starting wait_for_connection()")
    A2_connection = wait_for_connection(hostname, username, password, database )
    # A2_connection = pymysql.connect( host=hostname, user=username, passwd=password, db=database )

    # csv file name
    filename = "log.csv"

    row_contents = []

    count = 0
    prev = 0
    diff = 0
    flag = 0


    log("DEBUG", "Beginning main() loop")
    while True:
        
        try:
            # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
            # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
            # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
            
            if DEBUG:
                np_arr8_string = hx.get_np_arr8_string()
                binary_string = hx.get_binary_string()
                log("DEBUG", binary_string + " " + np_arr8_string)
            
            log("DEBUG", "Getting weight...")
            # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
            val = hx.get_weight(5)
            lb = val*.0022
            diff = lb - prev

            log("DEBUG", "raw value: %f, lb: %f, prev: %f, diff: %1.2f" % (val, lb, prev, diff))

            if diff > .01:              #accounting for fluxuations from weight sensor readings

                log("DEBUG", "Weight threshold met.")

                roundedDiff = round(diff,2)

                timeStamp = datetime.now()         #finding the time

                row_contents = [timeStamp.strftime("%x"),timeStamp.strftime("%X"),str(roundedDiff)]       #setting the values for the new row entry
                log("DEBUG", "Row Contents:" + ", ".join(row_contents))

                append_list_as_row(filename, row_contents)      #appending new row entry to the log.csv

                cur = A2_connection.cursor()
                A2_sql_insert = insert = "INSERT INTO t1(date, time, weight) VALUES ('%s', '%s', '%1.2f');" % (timeStamp.strftime("%Y-%m-%d"), timeStamp.strftime("%H:%M:%S"), float(roundedDiff))
                commit = "COMMIT;"

                log("DEBUG", "Executing SQL Insert" + A2_sql_insert)

                cur.execute( A2_sql_insert )
                cur.execute( commit )


                # select = "SELECT * FROM t1;"
                # cur.execute( select )

                # print("–––––––––––––––––––––––––––––––––")
                # print("|","date","|","time","|","weight","|")
                # print("–––––––––––––––––––––––––––––––––")
                # for x in cur.fetchall():
                #     print("|",x[0],"|",x[1],"|",x[2],"|")
                # print("–––––––––––––––––––––––––––––––––")

                
                
                count+=1                       #counts the number of drops and 
                log("DEBUG", "Number of drops: %d" % count)



            if count == 30:             #send reminder to empty box
                log("DEBUG", "Sending reminder")
                sending_reminder()
                count -= 5

            prev = lb
            log("DEBUG", "New weight: %d" % prev)

            # To get weight from both channels (if you have load cells hooked up 
            # to both channel A and B), do something like this
            #val_A = hx.get_weight_A(5)
            #val_B = hx.get_weight_B(5)
            #print "A: %s  B: %s" % ( val_A, val_B )
            
            hx.power_down()
            hx.power_up()

            log("DEBUG", "sleeping between drops...")
            time.sleep(15) #NOTE: fix this, too long in between weight calculations
            log("DEBUG", "Resuming!")

            if datetime.today().day == 1 and flag == 0:     #send the csv email once on the First of every Month
                log("DEBUG", "sending CSV")
                sending_csv(filename)
                flag = 1
            elif datetime.today().day == 2 and flag == 1:                          #reset the flag on the day after
                log("DEBUG", "Resetting flag for sending the CSV")
                flag = 0


            if count > 0 and lb < 0 :
                log("DEBUG", "sleeping for removal...")
                time.sleep(300)
                log("DEBUG", "Resuming!")

                log("DEBUG", "Resetting and Taring")
                hx.reset()          #if officer meyer removes bin, give her 5 min to empty and replace bins. Then tare system and continue
                hx.tare()
                count = 0 
                log("DEBUG", "Total drops: %d" % count)

                sending_csv(filename)

        except (KeyboardInterrupt, SystemExit):
            log("ERROR", "Exception, stpping.")
            sending_error()                  #if moving log.py, make sure to use full directory in place of filename
            cleanAndExit()


if __name__ == "__main__":    
    log("INIT", "Starting main()")
    main()
