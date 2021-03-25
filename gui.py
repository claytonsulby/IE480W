# Import Required Library
from tkinter import *
from tkcalendar import Calendar
from datetime import datetime

import pymysql

# Global Variables
startDate = ""
endDate = ""

if __name__ == "__main__":

    # Create Object
    root = Tk()
    
    # Set geometry
    root.geometry("400x800")
    
    # Add Calender
    cal = Calendar(root, selectmode = 'day',
                year = 2020, month = 5,
                day = 22)
    
    cal.pack(pady = 20)
    

    
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
        # SELECT *
        # FROM `objects`
        # WHERE (date_field BETWEEN '2010-01-30 14:15:55' AND '2010-09-29 10:15:55')
        global startDate
        global endDate
        
        hostname = '70.32.23.81'
        username = 'psupresc_admin'
        password = 'nipdy1-zagpos-nuHxoz'
        database = 'psupresc_dropbox'
        
        conn = pymysql.connect( host=hostname, user=username, passwd=password, db=database )
        cur = conn.cursor()
        
        tempStartDate = datetime.strptime(startDate, '%m/%d/%y').strftime("%Y-%m-%d %H:%M:%S")
        tempEndDate = datetime.strptime(startDate, '%m/%d/%y').strftime("%Y-%m-%d %H:%M:%S")
        
        
        # select = "\
        #     SELECT * FROM t1 \
        #     WHERE (date BETWEEN '%s' AND '%s') \
        #     INTO OUTFILE './log.csv' \
        #     FIELDS TERMINATED BY ',' \
        #     ENCLOSED BY '\"' \
        #     LINES TERMINATED BY '\n';" % (tempStartDate, tempEndDate)
        
        # select = "SELECT * FROM t1\
        #     INTO OUTFILE './log.csv' \
        #     FIELDS TERMINATED BY ',' \
        #     ENCLOSED BY '\"' \
        #     LINES TERMINATED BY '\n';"
        
        select = "SELECT * FROM t1 WHERE (date BETWEEN '%s' AND '%s');" % (tempStartDate, tempEndDate)
        
        # select = "SELECT * FROM t1;"
        
        cur.execute(select)
        
        print("–––––––––––––––––––––––––––––––––")
        print("|","date","|","time","|","weight","|")
        print("–––––––––––––––––––––––––––––––––")
        for x in cur.fetchall():
            print("|",x[0],"|",x[1],"|",x[2],"|")
        print("–––––––––––––––––––––––––––––––––")
        
        

    def grad_date():
        date.config(text = "Selected Date is: " + cal.get_date())
    
    # Add Button and Label
    Button(root, text = "Get Date",
        command = grad_date).pack(pady = 20)
    
    date = Label(root, text = "")
    date.pack(pady = 20)


    def startDateButtonCommand():
        
        global startDate
        global endDate
        
        setStartDate()
        startDateLabel.config(text = startDate)
        
    def endDateButtonCommand():
        
        global startDate
        global endDate
        
        setEndDate()
        endDateLabel.config(text = endDate)


    startDateLabel = Label(root, text = "")
    startDateLabel.pack()
    Button(root,text="Start Date",command= lambda: startDateButtonCommand()).pack()
    endDateLabel = Label(root, text = "")
    endDateLabel.pack()
    Button(root,text="End Date",command= lambda: endDateButtonCommand()).pack(pady = 20)
    
    Button(root,text="Query",command= lambda: selectToCSV()).pack()
    
    # Excecute Tkinter
    root.mainloop()