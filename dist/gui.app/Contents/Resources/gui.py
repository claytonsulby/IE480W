# Import Required Library
from tkinter import *
from tkcalendar import Calendar
import tksheet
from datetime import datetime
import csv

import pymysql

# Global Variables
startDate = ""
endDate = ""

log = []

if __name__ == "__main__":

    def updateList():
        listbox.delete(0, END)
        list = selectToCSV()
        i = 0
        listbox.insert(END, ['index', 'date', 'time', 'weight'])
        for row in list:
            x = [i] + row[1:]
            listbox.insert(END, x)
            i += 1

    def setStartDate():
        """ 
        Gets the startDate from the calendar.
        If the endDate is before the startDate, they flip.
        """
        global startDate
        global endDate
        
        if endDate != "":
            tempStartDate = datetime.strptime(cal.get_date(), '%m/%d/%y')
            tempEndDate = datetime.strptime(endDate, '%m/%d/%y')
            
            if tempEndDate < tempStartDate :
                startDate = endDate
                endDate = cal.get_date()
            else:
                startDate = cal.get_date()
        else:
            startDate = cal.get_date()
            
        return startDate
        
    def setEndDate():
        """ 
        Gets the endDate from the calendar.
        If the startDate is after the endDate, they flip.
        """
        global startDate
        global endDate
        
        if startDate != "":
            tempStartDate = datetime.strptime(startDate, '%m/%d/%y')
            tempEndDate = datetime.strptime(cal.get_date(), '%m/%d/%y')
            
            if tempStartDate > tempEndDate:
                endDate = startDate
                startDate = cal.get_date()
            else:
                endDate = cal.get_date()
        else:
            endDate = cal.get_date()
            
        return endDate
    
    def selectToCSV():
        global startDate
        global endDate
        
        hostname = '70.32.23.81'
        username = 'psupresc_admin'
        password = 'nipdy1-zagpos-nuHxoz'
        database = 'psupresc_dropbox'
        
        conn = pymysql.connect( host=hostname, user=username, passwd=password, db=database )
        cur = conn.cursor()
        
        tempStartDate = datetime.strptime(startDate, '%m/%d/%y').strftime("%Y-%m-%d %H:%M:%S")
        tempEndDate = datetime.strptime(endDate, '%m/%d/%y').strftime("%Y-%m-%d %H:%M:%S")
        
        select = "SELECT * FROM t1 WHERE date BETWEEN '%s' AND '%s';" % (tempStartDate, tempEndDate)
        
        # select = "SELECT * FROM t1;"
        
        cur.execute(select)

        output = []


        with open('log.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['report date', 'date', 'time', 'weight'])
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for x in cur.fetchall():
                output.append([now] + list(x))
                writer.writerow([now] + list(x))
        
        return output

    def startDateButtonCommand():
        
        global startDate
        global endDate
        
        setStartDate()
        startDateLabel.config(text = startDate)
        
        log.append("[LOG] Start Date: %s" % startDate)
        root.update()
        
    def endDateButtonCommand():
        
        global startDate
        global endDate
        
        setEndDate()
        endDateLabel.config(text = endDate)
        
        log.append("[LOG] End Date: %s" % endDate)
        root.update()
        
    def queryButtonCommand():
        
        global startDate
        global endDate

        updateList()


    # Create window object
    root = Tk()
    
    # Calender
    cal = Calendar(root, selectmode = 'day',year = datetime.now().year, month = datetime.now().month,day = datetime.now().day)
    
    
    startButton = Button(root,text="Start Date",command= lambda: startDateButtonCommand())
    startDateLabel = Label(root, text = "")
    
    
    endButton = Button(root,text="End Date", background='white',command= lambda: endDateButtonCommand())
    endDateLabel = Label(root, text = "")
    

    
    queryButton = Button(root,text="Query",command= lambda: queryButtonCommand())
    
    
    listbox = Listbox(root, height=8, width=50, border=0)
    scrollbar = Scrollbar(root)
    
    listbox.configure(yscrollcommand=scrollbar.set)
    scrollbar.configure(command=listbox.yview)
    
    
    
    cal.grid(row=0, column=0, rowspan = 3, columnspan=2)
    
    startDateLabel.grid(row=0, column=4, sticky=NW)
    endDateLabel.grid(row=1, column=4,sticky=NW)
    
    startButton.grid(row=0, column=3, sticky=NW)
    endButton.grid(row=1, column=3, sticky=NW)
    
    queryButton.grid(row=3, column=3, columnspan=2)
    
    listbox.grid(row=4, column=0, columnspan=4, rowspan=6, sticky=NS)
    scrollbar.grid(row=4, rowspan=6, column=4, sticky=NS)
    
    root.title('Opioid Takeback Query')
    root.geometry('500x350')
    
    # Excecute Tkinter
    root.mainloop()