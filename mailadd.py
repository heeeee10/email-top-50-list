#-*- coding:utf-8 -*-

import MySQLdb
import datetime
import os
import mmap


#this is our global vairables
db = MySQLdb.connect("localhost","testxqw","","testdb")
StartTime = datetime.datetime.now()
cwd = os.getcwd()
cursor = db.cursor()
cursor2 = db.cursor()

#function: insert data into databs
def readfiintoTable():
    cursor.execute("drop table if exists mailing")
    cursor.execute("create table mailing(addr VARCHAR(255))")
    path = os.path.join(cwd, "emails.txt")
    with open(path, 'r+b') as f:
        pointerf=mmap.mmap(f.fileno(), 0)
        while True:
            try:
                eachline = pointerf.readline().rstrip().decode("utf-8")
                if eachline:
                    adddom = eachline.split(',')
                    sql = '''INSERT INTO mailing(addr) VALUES ('%s')''' % adddom[1]
                    print adddom[1]
                    cursor.execute(sql) 
                else: 
                    break
                
            except Exception as e:
                raise e
                break
        db.commit()
        print "insert finish!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        pointerf.close()


#as I don't have daily email, I assume that the content of eamils.txt is the total emails during last 30 days
def getCurrenttop50():
    today = datetime.date.today()
    print today
    DD = datetime.timedelta(30)
    print DD
    previous = today - DD
    print previous
    cursor.execute("select count(*) from mailing")
    a=0
    for row in cursor.fetchall(): # a is the total number of emails during last 30days
        a = row[0]                #here it is useless
    cursor.execute("drop table if exists currenttop50")
    cursor.execute("create table currenttop50(Domain VARCHAR(255), Total INT)")
    sql = '''select substring_index(addr, '@', -1) as Domain, count(*) as Total from mailing
    group by Domain                 
    order by Total desc
        limit 50'''                 # get the top 50 domains in mysql and query them from table in database
    cursor.execute(sql)
    
    alladd = cursor.fetchall()
    for row in alladd:          #insert the data into currenttop50 table
        sql_insert = "insert into currenttop50(Domain, Total) values('%s', %s)" % (row[0], row[1])
        cursor.execute(sql_insert)
        db.commit()
    


#write the report    here we ignore calculation of the percentage since the number of total emails is fixed
def writereport():
    try:
        path = os.path.join(cwd, "top50report.txt")
        template = "{0:9}|{1:14}|{2:}"
        headfile = "The top 50 domains by count sorted by percentage of growth compared to total\n\n"
        strline = template.format("Percentage", "Count Number", "Domains\n")
        sql = "select * from currenttop50"
        cursor.execute(sql)
        lines = cursor.fetchall()
        for row in lines:
            strline += template.format( "n/a".rjust(7), str(row[1]).rjust(7), row[0]) + "\n"
            print str(row[1]) + "\t" + str(row[0])
        with open(path, 'w') as w:
                w.write(headfile + strline)
    except Exception as e:
        raise e

        
        
def main():
    starttime = datetime.datetime.now()
    print "!!!!!!!!!!!!!!!now we start insert behavior and the time is: %s" % str(starttime)
    readfiintoTable()
    starttop = datetime.datetime.now()
    print "!!!!!!!!!!!!!!!now we start get the top50 domains, the time is: %s" % str(starttop)
    getCurrenttop50()
    startreport = datetime.datetime.now()
    print "!!!!!!!!!!!!!!!now we write the report, and the time is: %s" % str(startreport)
    writereport()
    finishtime = datetime.datetime.now()
    print "!!!!!!!!!!!!!!!game is finished!!!!!!!! time is: %s" % str(finishtime)
        
if __name__ == '__main__':
    main()
