import csv 
from csv import writer
from datetime import datetime

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


sender_email = 'psu.prescriptiondropbox@gmail.com'
password = 'xafze5-tAsted-jaznix'
receiver_emails = ["claytonsulby@gmail.com", "cls6275@psu.edu"]

def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)



def sending_csv (file):
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)
    monthStamp = datetime.now()         #finding the time
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

    email_session.sendmail(sender_email,receiver_email,my_message)
    email_session.quit()



def sending_reminder():
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)
    message["Subject"] = "Empty Prescription DropBox"

    Body = "30+ Prescription drops have been made! Please empty as soon as possible."
    

    email_session = smtplib.SMTP('smtp.gmail.com',587)
    email_session.ehlo()
    email_session.starttls()
    email_session.login(sender_email, password)

    email_session.sendmail(sender_email,receiver_email, Body)
    email_session.quit()



def sending_error():
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ", ".join(receiver_emails)
    message["Subject"] = "Reset System ASAP"

    my_message = "The Raspberry Pi has malfunctioned and needs to be reset as soon as possible. Please press the power button twice so that the red light turns off and on again.\n\nThank you!"

    email_session = smtplib.SMTP('smtp.gmail.com',587)
    email_session.ehlo()
    email_session.starttls()
    email_session.login(sender_email, password)

    email_session.sendmail(sender_email,receiver_email,my_message)
    email_session.quit()