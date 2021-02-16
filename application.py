#-------------------------------------------------------------------------------
# Name:        ENGO 551 ab 1
# Student:      Tanya Hegmann
# Created:     11-02-2021
#-------------------------------------------------------------------------------

import os
import csv #added on for csv read in
import json #built in json package to work with data


#import requests #as provided in lab to acess requests for json
##import sys
##sys.path.insert(0, 'C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\Lib\site-packages\requests')
import requests


from flask import Flask, session, render_template, request, jsonify #Note added in request & render_template as they do in the lectures
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL")) #Already preset as enviro variable
#postgres://hittsqstabxgpv:edfab3a728220ef17e540ebb509e91c46a8fb41af43fb845ecb30ff16b7be7ce@ec2-52-7-168-69.compute-1.amazonaws.com:5432/dfafkrpfvhk650
db = scoped_session(sessionmaker(bind=engine)) #main object to run SQL commands

#---------------------------------------------------------------------
#HOMEPAGE

@app.route("/")
def index():

##    if 'username' in session:
##        username = session['username']
##        return "Logged in as " + username + '<br>' + "<b><a href = '/logout'>click here to log out</a></b>"
##
##    return "You are not logged in <br><a href = '/login'></b>" + "click here to log in</b></a>"

    if 'username' in session: #check if currently signed in
        username = session['username']
        return render_template("homesignedin.html", username = username)

    return render_template("home.html")

    #return render_template("baseindex.html")


#---------------------------------------------------------------------
#Test Page for testing functions

@app.route("/87")
def baseindex():
# Test page for debugging code

##    testusername = "orange"
##    testpassword = "apple"
##    db.execute("INSERT INTO testuserinfo (username, password) VALUES (:username, :password)",{"username":testusername, "password":testpassword})
##    db.commit()#commit changes

    #book_info = request.get_json("https://www.googleapis.com/books/v1/volumes/080213825X", force = True)


    return x

#---------------------------------------------------------------------

@app.route("/api/<string:ISBN>")
def ISBNroute(ISBN):

    apisearch = ISBN
    book_info = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": "isbn:"+apisearch}) #Combine strings for full parameters based on variable input
    #book_info = request.get_json("https://www.googleapis.com/books/v1/volumes/080213825X", force)
    book_json = book_info.json() #quickly search json info for comparison to check if it exists or not

    Totalitems = book_json['totalItems']

    if Totalitems == 0 : #ie, if 0 total items aka if no results
        #No result for the ISBN exists for google books, try again go back to search page
        return render_template("googlebooksapisearchnone.html", apisearch = apisearch)

    #else it does exist

    #extra data or try to pass in
    try:
        Title = list(book_json.values())[2][0]['volumeInfo']['title']
    except:
        Title = "Null"

    try:
        Author = list(book_json.values())[2][0]['volumeInfo']['authors'][0]
    except:
        Author = "Null"

    try:
        PublishedDate = list(book_json.values())[2][0]['volumeInfo']['publishedDate']
    except:
        PublishedDate = "Null"

    try:
        ISBN10 = list(book_json.values())[2][0]['volumeInfo']['industryIdentifiers'][1]['identifier']
    except:
        ISBN10 = "Null"

    try:
        ISBN13 = list(book_json.values())[2][0]['volumeInfo']['industryIdentifiers'][0]['identifier']
    except:
        ISBN13 = "Null"

    try:
        RatingsCount = list(book_json.values())[2][0]['volumeInfo']['ratingsCount']
    except:
        RatingsCount = "Null"

    try:
        AvgRating = list(book_json.values())[2][0]['volumeInfo']['averageRating']
    except:
        AvgRating = "Null"



    #return "The ISBN Number is, {ISBNhere}!".format(ISBNhere = ISBN)
    return jsonify({ "title": Title, "author": Author, "publishedDate": PublishedDate, "ISBN_10": ISBN10, "ISBN_13": ISBN13, "reviewCount": RatingsCount, "averageRating": AvgRating })

#---------------------------------------------------------------------
# LOG IN/SIGN IN PAGE

@app.route("/signin")
def signin():

    return render_template("signin.html")

#---------------------------------------------------------------------
# CHECK LOG IN/SIGN IN PAGE

@app.route("/signincheck", methods=["POST"])
def signincheck():
    #check against database here

    #Assign temp variables to use as comparisons
    username = request.form.get("username_old")
    password = request.form.get("password_old")

    #Check against database

    checkuser = db.execute("SELECT * FROM testuserinfo WHERE (username = '{username}') AND (password = '{password}')".format(username = username, password = password)).fetchone()

    #if return false
    if checkuser is None:
        #ERROR SIGN IN TEMPLATE RUN
        return render_template("signinfail.html", username = username, password = password)

    #else if return true

    #start session
    session["user"] = username

    #run correct sign in
    return render_template("signinverify.html", username = username, password = password)

#---------------------------------------------------------------------
# SIGN UP PAGE

@app.route("/signup")
def signup():

    return render_template("signup.html")

#---------------------------------------------------------------------
# CHECK SIGN UP PAGE

@app.route("/signupcheck", methods=["POST"])
def signupcheck():
    #check against database here

    #Assign temp variables to use as comparisons
    username = request.form.get("username_new")
    password = request.form.get("password_new")

    #Check against database if Username already exists
    #Only need to check if username exists
    checkuser = db.execute("SELECT * FROM testuserinfo WHERE (username = '{username}')".format(username = username)).fetchone()

    #If username exists
        #error try again page

    #If Username does not already exist
    if checkuser is None:
        #Add Data to List
        db.execute("INSERT INTO testuserinfo (username, password) VALUES (:username, :password)",{"username":username, "password":password})
        db.commit()#commit changes

        #start session
        session["user"] = username

        return render_template("signupverify.html", username = username, password = password)

    #else if return true (aka username already exists)
    #run failed sign in
    return render_template("signupfail.html", username = username, password = password)


#---------------------------------------------------------------------
# IMPORT BOOKS EXCEL FOR QUESTION 4

@app.route("/import_lab1_question4_books") #long name don't want users to acidently stumble upon but is required for
def importexcelbooks():
    #import books from books.csv into a database


    #check if already been imported by checking if entry in there (don't want to double import every time run page)

    #isbn to check (first entry from excel)
    isbnbook = "1416949658"

    checkuser = db.execute("SELECT * FROM excelbooks WHERE (isbn = '{isbn}')".format(isbn = isbnbook)).fetchone()


    if checkuser is None: #if not already uploaded
        #Upload
        opencsv = open("books.csv")
        bookreader = csv.reader(opencsv)

        #import values
        for isbn, title, author, year in bookreader:
            db.execute("INSERT INTO excelbooks (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",{"isbn":isbn, "title":title, "author":author, "year":year})
        db.commit()#commit changes

        textvar = "books.csv Has Been Uploaded"
        return render_template("proofofupload.html", textvar = textvar) #quick page for compleation of upload and screenshot proof of import sucsess

    #else already uploaded
    textvar = "books.csv Has Already Been Uploaded"
    return render_template("proofofupload.html", textvar = textvar) #quick page for compleation of upload and screenshot proof of import sucsess


#---------------------------------------------------------------------
# BOOK SEARCH PAGE


@app.route("/booksearch", methods=["POST"])
def booksearch():

    #retrieve session info
    username = session["user"]

    return render_template("booksearch.html", username = username) #load book search page



#---------------------------------------------------------------------
# LOGOUT PAGE

@app.route("/logout", methods=["POST"])
def logout():

    username = session["user"] #retrieve username

    session.pop("user", None) #remove session, log out
    session.pop("book", None) #remove session data

    return render_template("userlogout.html", username = username) #load book search page




#---------------------------------------------------------------------
# ISBN SEARCH RESULTS

@app.route("/isbnsearch", methods=["POST"])
def isbnsearch():

    #pass in isbn to search from prev search
    isbntosearch = request.form.get("isbn_search")

    #SQL search based on our books database for results including partial
    #Can use LIKE for partial matches, and use the joined %_result_% for partial searches
    isbnsearchresults = db.execute("SELECT isbn, title, author, year FROM excelbooks WHERE isbn LIKE (:isbntosearch)",{"isbntosearch":("%"+isbntosearch+"%")}).fetchall()
    #isbnsearchresults = db.execute("SELECT isbn, title, author, year FROM excelbooks WHERE isbn = '1416949658'").fetchall() #debug test

    #If found none
    if not isbnsearchresults: #if list is empty aka no results
        return render_template("isbnsearchnone.html", isbnsearchresults = isbnsearchresults, isbntosearch = isbntosearch)#pass in search results as a variable

    #else, render results
    return render_template("isbnsearch.html", isbnsearchresults = isbnsearchresults, isbntosearch = isbntosearch)#pass in search results as a variable


#---------------------------------------------------------------------
# TITLE SEARCH RESULTS

@app.route("/titlesearch", methods=["POST"])
def titlesearch():

    #pass in isbn to search from prev search
    titletosearch = request.form.get("title_search")

    #SQL search based on our books database for results including partial
    #Can use LIKE for partial matches, and use the joined %_result_% for partial searches
    #lower(query) returns the search as if they were all lowercase so its not case-sensitive depending on the input
    titlesearchresults = db.execute("SELECT isbn, title, author, year FROM excelbooks WHERE lower(title) LIKE lower((:titletosearch))",{"titletosearch":("%"+titletosearch+"%")}).fetchall()

    #If found none
    if not titlesearchresults: #if list is empty aka no results
        return render_template("titlesearchnone.html", titlesearchresults = titlesearchresults, titletosearch = titletosearch)#pass in search results as a variable

    #else, render results
    return render_template("titlesearch.html", titlesearchresults = titlesearchresults, titletosearch = titletosearch)#pass in search results as a variable


#---------------------------------------------------------------------
# AUTHOR SEARCH RESULTS

@app.route("/authorsearch", methods=["POST"])
def authorsearch():

    #pass in isbn to search from prev search
    authortosearch = request.form.get("author_search")

    #SQL search based on our books database for results including partial
    #Can use LIKE for partial matches, and use the joined %_result_% for partial searches
    #lower(query) returns the search as if they were all lowercase so its not case-sensitive depending on the input
    authorsearchresults = db.execute("SELECT isbn, title, author, year FROM excelbooks WHERE lower(author) LIKE lower((:authortosearch))",{"authortosearch":("%"+authortosearch+"%")}).fetchall()

    #If found none
    if not authorsearchresults: #if list is empty aka no results
        return render_template("authorsearchnone.html", authorsearchresults = authorsearchresults, authortosearch = authortosearch)#pass in search results as a variable

    #else, render results
    return render_template("authorsearch.html", authorsearchresults = authorsearchresults, authortosearch = authortosearch)#pass in search results as a variablel



#---------------------------------------------------------------------
# GOOGLE BOOKS API SEARCH

@app.route("/googlebooksapisearch", methods=["POST"])
def googlebooksapisearch():

    apisearch = request.form.get("googlebooks_search")
    book_info = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": "isbn:"+apisearch}) #Combine strings for full parameters based on variable input
    #book_info = request.get_json("https://www.googleapis.com/books/v1/volumes/080213825X", force)
    book_json = book_info.json() #quickly search json info for comparison to check if it exists or not

    Totalitems = book_json['totalItems']

    if Totalitems == 0 : #ie, if 0 total items aka if no results
        #No result for the ISBN exists for google books, try again go back to search page
        return render_template("googlebooksapisearchnone.html", apisearch = apisearch)

    #else it does exist

    #extra data or try to pass in
    try:
        Title = list(book_json.values())[2][0]['volumeInfo']['title']
    except:
        Title = "Null"

    try:
        Author = list(book_json.values())[2][0]['volumeInfo']['authors'][0]
    except:
        Author = "Null"

    try:
        PublishedDate = list(book_json.values())[2][0]['volumeInfo']['publishedDate']
    except:
        PublishedDate = "Null"

    try:
        ISBN10 = list(book_json.values())[2][0]['volumeInfo']['industryIdentifiers'][1]['identifier']
    except:
        ISBN10 = "Null"

    try:
        ISBN13 = list(book_json.values())[2][0]['volumeInfo']['industryIdentifiers'][0]['identifier']
    except:
        ISBN13 = "Null"

    try:
        RatingsCount = list(book_json.values())[2][0]['volumeInfo']['ratingsCount']
    except:
        RatingsCount = "Null"

    try:
        AvgRating = list(book_json.values())[2][0]['volumeInfo']['averageRating']
    except:
        AvgRating = "Null"

    #render a page with the link to go to with lots ot pass in
    return render_template("googlebooksapisearch.html", apisearch = apisearch, book_json = book_json, Title = Title, Author = Author, PublishedDate = PublishedDate, ISBN10 = ISBN10, ISBN13 = ISBN13, RatingsCount = RatingsCount, AvgRating = AvgRating)


#---------------------------------------------------------------------
# RESULTING PAGE OF ISBN BOOK SEARCH

@app.route("/bookresult", methods=["POST"])
def bookresult():

    search_results = request.form.get("search_results")#Pull in selection from last time, contains full ISBN even if last time was partial

    #If returning from a button aka no new entry
    if search_results is None:
        search_results = session["book"] #retrieve instead from session info which would have been saved

    bookdata = db.execute("SELECT isbn, title, author, year FROM excelbooks WHERE isbn = (:isbn)",{"isbn":search_results})
    #bookdata = db.execute("SELECT isbn, title, author, year FROM excelbooks WHERE isbn = '1416949658'") #debug

    username = session["user"] #retrieving username to pass in

    #save here the book being looked at so can return here after loop, save as a session
    session["book"] = search_results

    #Get content for any pre-posted reviews
    currentisbn = search_results
    reviews = db.execute("SELECT isbn, username, ratingscale, review FROM websitereviews WHERE isbn = (:isbn)",{"isbn":search_results}).fetchall()

    #Retrieve google books review data
    apisearch = search_results
    book_info = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": "isbn:"+apisearch}) #Combine strings for full parameters based on variable input
    book_json = book_info.json() #quickly search json info for comparison to check if it exists or not

    #extra data or try to pass in
    try:
        RatingsCount = list(book_json.values())[2][0]['volumeInfo']['ratingsCount']
    except:
        RatingsCount = "Null"
    try:
        AvgRating = list(book_json.values())[2][0]['volumeInfo']['averageRating']
    except:
        AvgRating = "Null"

    return render_template("bookresult.html", RatingsCount = RatingsCount, AvgRating = AvgRating, search_results = search_results, bookdatasearchresults = bookdata, username = username, reviews = reviews)#pass in search results as a variable

#---------------------------------------------------------------------
# REVIEW CHECK
@app.route("/reviewprocess", methods=["POST"])
def reviewprocess():


    username = session["user"] #retrieving username to pass in
    bookisbn = session["book"] #retrieve book isbn for review

    ratingscale = request.form.get("reviewnumber")
    review = request.form.get("review")

   #Check if review been posted or not by checking username and isbn aka if someone submit a review to this isbn yet
    reviewsearchresults = db.execute("SELECT isbn, username, ratingscale,review FROM websitereviews WHERE (isbn LIKE (:isbntosearch)) AND (username = (:username))" ,{"isbntosearch":("%"+bookisbn+"%"), "username":username}).fetchall()


    #If found none

    if not reviewsearchresults: #if list is empty aka no results
        #add new review
        db.execute("INSERT INTO websitereviews (isbn, username,ratingscale,review) VALUES (:isbn, :username, :ratingscale, :review)",{"isbn": bookisbn, "username":username, "ratingscale":ratingscale, "review":review})
        db.commit()#commit changes
        return render_template("reviewprocessconfirm.html", username = username, book=bookisbn)

    #else if review was found
    return render_template("reviewprocessfail.html", username = username, book=bookisbn)
























