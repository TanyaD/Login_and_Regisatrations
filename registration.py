from flask import Flask, render_template, request, redirect, flash, session
app=Flask(__name__)
app.secret_key='secrlksj'
from mysqlconnection import MySQLConnector
mysql = MySQLConnector(app, 'registrationdb')
import os, binascii
import md5


import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NAME_REGEX = re.compile(r'^([^0-9]*)$')




@app.route('/')
def index():
    return render_template('index.html', type1='hidden')

@app.route('/success_post', methods=['POST'])
def pass_data():
    fname= request.form['fname']
    lname= request.form['lname']
    email= request.form['email']
    password= request.form['password']
    password_two= request.form['confirm_password']
    salt =  binascii.b2a_hex(os.urandom(15))
    hashed_pw = md5.new(password + salt).hexdigest()

    if len(request.form['fname'])<1:
        flash('First Name cannot be empty!')
        return redirect('/')
    if not NAME_REGEX.match(request.form['fname']):
        flash("No numbers accepted in First Name!")
        return redirect('/')
    #send first name to DB

    #lastname
    if len(request.form['lname']) < 1:
        flash("Last Name cannot be empty!")
        return redirect('/')
    if not NAME_REGEX.match(request.form['lname']):
        flash("No numbers accepted in Last Name!")
        return redirect('/')
    #validate email format
    if len(request.form['email']) < 1:
        flash("Email cannot be empty!")
        return redirect('/')
    if not EMAIL_REGEX.match(request.form['email']):
        flash("Email Address should look like email@email.com!")
        return redirect('/')
    #validate email in DB
    email_value=request.form['email']
    data = {'email': email_value}
    query = "SELECT email FROM registrations WHERE email = :email"
    result=mysql.query_db(query, data)
    if result != []:
        flash("Email invalid, user already exists")
        return redirect('/')

    #password
    if len(request.form['password']) < 1:
        flash("Pwd cannot be empty!")
        return redirect('/')
    if len(request.form['password']) < 8:
        flash("Password should be more than 8 characters")
        return redirect('/')
    #confirm_password
    if len(request.form['confirm_password']) < 1:
        flash("Pwd cannot be empty!")
        return redirect('/')
    if request.form['confirm_password']!=request.form['password']:
        flash("Pwd should match!")
        return redirect('/')

    
    query = "INSERT INTO registrations (first_name, last_name, email, password, salt) VALUES (:first_name, :last_name, :email, :hashed_pw, :salt)"
    #We'll then create a dictionary of data from the POST data received.
    data = {
        'first_name': request.form['fname'],
        'last_name':  request.form['lname'],
        'email': request.form['email'],
        'hashed_pw': hashed_pw,
        'salt': salt
    }
    mysql.query_db(query, data)

    return redirect('/success')
       
@app.route('/success')
def sucess():
    return  render_template('success.html')
    
@app.route('/login', methods=['POST'])
def login():
    email=request.form['login_email']
    password=request.form['login_password']
    user_query = "SELECT * FROM registrations WHERE registrations.email = :email LIMIT 1"
    query_data = {'email': email}
    user = mysql.query_db(user_query, query_data)

    if len(request.form['login_email']) < 1:
        flash("Email cannot be empty!")
        return redirect('/')
    if not EMAIL_REGEX.match(request.form['login_email']):
        flash("Email Address should look like email@email.com!")
        return redirect('/')
    if len(request.form['login_password']) < 1:
        flash("Pwd cannot be empty!")
        return redirect('/')

    if user == []:
        flash("User doesn't exist")
        return redirect('/')

    if user[0]['password'] == md5.new(password + user[0]['salt']).hexdigest():
        return redirect('/success')
    
    flash("Password invalid")
    return redirect('/')







app.run(debug=True)




