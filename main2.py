# Imports
from flask import render_template, flash, redirect, url_for, request, Flask, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from wtforms import Form, StringField, DateTimeField, TextField, PasswordField, validators, SubmitField, TextAreaField, RadioField, IntegerField, FloatField, FileField, SelectField
from wtforms.fields.html5 import DateField
from wtforms.validators import ValidationError, DataRequired, EqualTo
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
import sys
import pymysql 
import sqlite3
import getpass
from email.message import EmailMessage
import smtplib
from email.mime.text import MIMEText
import uuid
from werkzeug.utils import secure_filename
import os
import datetime
import re

# Connect to Database

db = pymysql.connect(host='localhost', user='root', password='root', db='HIPS')
c = db.cursor()

# execute scripts from file function

def executeScriptsFromFile(filename):
	fd = open(filename, 'r')
	sqlFile = fd.read()
	fd.close()
	sqlCommands = sqlFile.split(';')

	for command in sqlCommands:
		try:
			if command.strip() != '':
				c.execute(command)
		except (IOError):
			print ("Command skipped: ")
	db.commit()
			

## FLASK FORMS subclassed from FlaskForm


class LoginForm(FlaskForm):
	username = TextField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	submit = SubmitField('Sign In')

class SignupForm(FlaskForm):
	username = TextField('Username', validators=[DataRequired()])
	#Add built in Validator
	password = PasswordField('Password', validators=[DataRequired(), EqualTo('confirmPass', message='Passwords must match')])
	confirmPass = PasswordField('Repeat Password', validators=[DataRequired()])
	submit = SubmitField('Sign Up')

class AddDeviceForm(FlaskForm):
	## Device Name, Type, IP Address, Type can be camera with sensor, camera w/out sensor, sensor, alarm 
	
	Device_Name = StringField('Device Manufacturer',validators=[DataRequired()])
	Device_Type = StringField('Device Type',validators=[DataRequired()])
	Device_IP = StringField('Device IP',validators=[DataRequired("Enter only the Numeric Values")])
	submit =  SubmitField('Submit: ')

class ViewDeviceForm(FlaskForm):
	Device_Name = SelectField('Device Name', choices= [], coerce=int)
	
class RemoveDeviceForm(FlaskForm):
	Device_Name = SelectField('Device Name', choices= [], coerce=int)
	submit =  SubmitField('Remove Device')
	

## User & device classes

class User(UserMixin):
	def __init__(self, username, password):
		self.id = username.replace("'", "")
		# hash the password and output it to stderr
		self.password = password


class Device():
	def __init__(self, Device_Name, Device_Type, Device_IP):
		self.id = Device_Name
		self.Device_Type = Device_Type
		self.Device_IP = Device_IP





## Creating the Flask app object and login manager

app = Flask(__name__)

skey = os.urandom(12)
app.config['SECRET_KEY'] = skey
bootstrap = Bootstrap(app)
moment = Moment(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'



# Code to load users and cars as functions to load later

def load_users():
	c.execute("SELECT * from user_table")
	users = c.fetchall()
	for user in users:
		user_db[user[1]]=user[2]	

	
def load_devices():
	c.execute("SELECT * from device_table")
	devices = c.fetchall()
	for device in devices:
		device_db[str(device[0])] = Device(device[0],device[1],device[2])		


# Initialize User and Device Databases

user_db = {}
device_db = {}

load_users()
load_devices()


# Check for User Name in DB
	
def profileIsSetup():
	if current_user.profileSetup == 1:
		return True
	else:
		return False
		


# Login manager uses this function to manage user sessions
# Function does a lookup by id and returns the User object if
# it exists, none otherwise

@login_manager.user_loader
def load_user(id):
	return User(id, user_db[id])
	
# Index Route
	
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():		
	form = ViewDeviceForm()
	load_devices()
	db = pymysql.connect(host='localhost', user='root', password='root', db='HIPS')
	c = db.cursor()
	c.execute('SELECT user_id FROM user_table WHERE User_Name="{}"'.format(current_user.id))
	user_id = c.fetchall()[0][0]
	c.execute('SELECT device_ID, Device_Name from device_table WHERE user_id = {}'.format(user_id))
	devices=c.fetchall()
	form.Device_Name.choices = devices
	return render_template ('index.html', form=form, devices=device_db.values())
		

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	# display the login form
	form = LoginForm()
	if form.validate_on_submit():
		user = form.username.data
		# validate user
		valid_password = user_db[form.username.data]
		if user is None or not valid_password:
			print('Invalid username or password', file=sys.stderr)
			redirect(url_for('index'))
		else:
			login_user(User (user, valid_password))
			flash('Login Successful', category='success')
			return redirect(url_for('index'))

	return render_template('login.html', title='Sign In', form=form)

# Sign Up Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	# display the Signup form
	form = SignupForm()
	if form.validate_on_submit():
		user = form.username.data
		exists = user_db.get(user)
		# validate user
		if exists is None:
			user_pass = form.password.data
			c.execute ('INSERT INTO user_table (user_id, User_Name, Password, User_Type) VALUES ({},"{}","{}","{}")'.format(0,user, user_pass, 'User'))
			db.commit()
			load_users()
			return redirect(url_for('index'))
		else:
			flash('Invalid User Name or Password', category='error')
			return redirect(url_for('index'))

	return render_template('signup.html', title='Sign Up', form=form)

# Add a Device Route
@app.route('/adddevice', methods=['GET', 'POST'])
def adddevice():
	form = AddDeviceForm()
	if form.validate_on_submit():
		Device_Name = form.Device_Name.data
		Device_Type = form.Device_Type.data
		Device_IP = form.Device_IP.data
		db = pymysql.connect(host='localhost', user='root', password='root', db='HIPS')
		c = db.cursor()
		c.execute ('SELECT user_id FROM user_table WHERE User_Name="{}"'.format(current_user.id))
		user_id= c.fetchall()[0][0]
		sql = ('INSERT INTO device_table (device_id, user_id, Device_Name, Device_Type, Device_IP) VALUES ({}, "{}","{}","{}","{}")'.format(0,user_id, Device_Name,Device_Type,Device_IP))
		c.execute (sql)
		db.commit()
		load_devices()
		return (redirect('/index'))
		
	return render_template('adddevice.html', title='Add Device', form=form)

@app.route('/removedevice',methods=['GET', 'POST'])
def removedevice():
	form = RemoveDeviceForm()
	load_devices()
	db = pymysql.connect(host='localhost', user='root', password='root', db='HIPS')
	c = db.cursor()
	c.execute('SELECT user_id FROM user_table WHERE User_Name="{}"'.format(current_user.id))
	user_id = c.fetchall()[0][0]
	c.execute('SELECT Device_ID, Device_Name FROM device_table WHERE user_id = {}'.format(user_id))
	devices=c.fetchall()
	form.Device_Name.choices = devices
	print(devices)
	print(user_id)
	if form.validate_on_submit():
		sql = "DELETE FROM device_table WHERE Device_ID = '{}'".format(form.Device_Name.data)
		c.execute (sql)
		db.commit()
		db.close()
		return (redirect('/index'))
	return render_template('removedevice.html', title='Remove Device', form=form)




# Logout Route
@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

# About Route
@app.route('/about')
def about():
	return render_template('about.html', title='About')

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=True)
	
