from django.shortcuts import render
from django.http import HttpResponse
import mysql.connector

def run(rq):

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        passwd="",
        database="test"
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT name FROM test")

    myresult = mycursor.fetchone()
    x = "<p>%s</p>" % myresult[0]

    return HttpResponse("Success -> "+x)