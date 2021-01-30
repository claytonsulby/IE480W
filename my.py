#! /usr/bin/python3

import time
import sys
import csv
from csv import writer import datetime import smtplib
from email.mime.multipart import MIMEMultipart from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import shutil
import os

EMULATE_HX711 = False   #change to false when HX711 is connected 

#referenceUnit = 1

sender_email = 'psu.prescriptiondropbox@gmail.com'
password = 'Password1!2@3#'
receiver_email = 'jbm203@psu.edu'
receiver_email2 = 'jbm203@psu.edu,pmg14@psu.edu,jaw900@psu.edu,dak27@psu.edu'

#if not EMULATE_HX711:
#   import RPi.GPIO as GPIO
#   from hx711 import HX711 
#else:
#   from emulated_hx711 import HX711

import RPi.GPIO as GPIO 
from hx711 import HX711

def cleanAndExit(): 
    print("Cleaning...")
    if not EMULATE_HX711: 
        GPIO.cleanup()
    
    print("Bye!")
    sys.exit()
    

################################################
# Function: append_list_as_row
# Inputs: filename to write to, list of elements to
# Output: N/A but file is updated
# Purpose: adding new lines to the csv for each drop and updating the log file in the USB stick
################################################

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)
    
    moving_log(file_name)


################################################
# Function: sending_csv
# Inputs: file to send to recipients
# Output: sends email to second list of recipients
# Purpose: sends email containing the latest version of the csv log file 
################################################

def sending_csv (file):
    message = MIMEMultipart()
    message["From"] = sender_email 
    message["To"] = receiver_email2 
    monthStamp = datetime.datetime.now()    #finding the time
    monthStamp = monthStamp.strftime("%B %Y")
    
    message["Subject"] = monthStamp + " Dropbox Log Update"     #find correct month and year
    
    attachment = open(file, 'rb')
    
    obj = MIMEBase('application','octet-stream')

    obj.set_payload((attachment).read())
    encoders.encode_base64(obj)
    obj.add_header('Content-Disposition',"attachment; filename= "+file)


    message.attach(obj)
    
    my_message = message.as_string()
    
    email_session = smtplib.SMTP('smtp.gmail.com',587)
    email_session.ehlo()
    email_session.starttls()
    email_session.login(sender_email, password)
    
    email_session.sendmail(sender_email,receiver_email2,my_message)
    email_session.quit()

################################################
# Function: sending_reminder
# Inputs: none
# Output: sends email to officer meyer to clear out box
# Purpose: remind the officer to empty the box so it does not overflow 
################################################

def sending_reminder():
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Empty Prescription DropBox"
    Body = "30+ Prescription drops have been made! Please empty as soon as possible."
    email_session = smtplib.SMTP('smtp.gmail.com',587)
    email_session.ehlo()
    email_session.starttls()
    email_session.login(sender_email, password)
    email_session.sendmail(sender_email,receiver_email, Body)
    email_session.quit()

################################################
# Function: sending_error
# Inputs: none
# Output: send email to officer meyer if something goes wrong
# Purpose: sending an email to the officer to reset the system if something occurs by pressing the on/off switch
################################################

def sending_error():
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Reset System ASAP"
    my_message = "The Raspberry Pi has malfunctioned and needs to be reset as soon as possible. Please press the power button twice so that the red light turns off and on again.\n\nThank you!"
    email_session = smtplib.SMTP('smtp.gmail.com',587)
    email_session.ehlo()
    email_session.starttls()
    email_session.login(sender_email, password)
    email_session.sendmail(sender_email,receiver_email,my_message)
    email_session.quit()

################################################
# Function: moving_log
# Inputs: file to copy over
# Output: copy of updated file in USB
# Purpose: updates the csv file in the USB stick for easy access to data 
################################################

def moving_log( file ):
    monthStamp = datetime.datetime.now()
    monthStamp = monthStamp.strftime("%B %Y")
    
    original = r'/home/pi/Documents/hx711py/log.csv'
    target = r'/media/pi/DROPBOX/log.csv'
    
    shutil.copy(original, target)

hx = HX711(5, 6)
hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFERENCE UNIT
#used reference weight of a bottle (2.25 lbs = 1020.56 grams) 
#displayed weight was 104675.111
#following rule of thirds, 104675.111 / 1020.56 = 102.56

hx.set_reference_unit(102)

#hx.set_reference_unit(referenceUnit)
#print("\n", referenceUnit)are system and

hx.reset()
hx.tare()
print("Tare done! Add weight now...")

# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()

###############################################################################
###############
#at end of example.py, move log.csv to different folder for officer meyer ease of use
#use new location to email to her 
###############################################################################
###############

# csv file name
filename = "log.csv"
row_contents = []
count = 0
prev = 0
diff = 0
flag = 0
while True:
    try:
        # These three lines are useful to debug whether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string
        
        # Prints the weight. Comment if you're debugging the MSB and LSB issue.
        val = hx.get_weight(5)
        lb = val*.0022
        #print(lb)
        
        diff = lb - prev
        
        if diff > .05: #accounting for fluxuations from weight sensor readings

            roundedDiff = round(diff,2)
            print(roundedDiff)
            timeStamp = datetime.datetime.now() #finding the time
            row_contents = [timeStamp.strftime("%x"),timeStamp.strftime("%X"),str(roundedDiff)] #setting the values for the new row entry
            append_list_as_row(filename, row_contents) #appending new row entry to the log.csv
            count+=1 #counts the number of drops
            
        if count == 30:  #send reminder to empty box
            #sending_reminder()
            count -= 5
        
        prev = lb

        # To get weight from both channels (if you have load cells hooked up # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        #print "A: %s B: %s" % ( val_A, val_B )
        hx.power_down()
        hx.power_up() 
        time.sleep(15)
        
        if datetime.datetime.today().day == 1 and flag == 0: #send the csv email once on the First of every Month
            #sending_csv(filename)
            flag = 1
        elif datetime.datetime.today().day == 2 and flag == 1: #reset the flag on the day after
            flag = 0
        if count > 0 and lb < .03 :
            time.sleep(300) #if officer meyer removes bin, give her 5 min to empty and replace bins, Then continue
            hx.reset()
            hx.tare()
            count = 0
    except (KeyboardInterrupt, SystemExit):
        # sending_error() #if moving log.py, make sure to use full directory in place of filename
        cleanAndExit()

# remove # from start of the mail related lines when connected to constant wifi connection for emails to be sent:
#
# to end program from running in background, scroll down in the following link to the troubleshooting portion
# use 'systemctl status weight.service' to check service status #
# https://learn.sparkfun.com/tutorials/how-to-run-a-raspberry-pi-program-on-startup/all
#
#
#always power off Raspberry Pi before removing the USB stick