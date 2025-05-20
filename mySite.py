# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response
#from werkzeug import secure_filename
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from supportFile import *
import utils
import os
import cv2
import nltk
import sqlite3
from datetime import datetime
import pandas as pd

app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def landing():
	return render_template('home.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
	return render_template('home.html')

@app.route('/info', methods=['GET', 'POST'])
def info():
	return render_template('info.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			num = request.form['num']
			
			users = {'Name':request.form['name'],'Email':request.form['email'],'Contact':request.form['num']}
			df = pd.DataFrame(users,index=[0])
			df.to_csv('users.csv',mode='a',header=False)

			sec = {'num':num}
			df = pd.DataFrame(sec,index=[0])
			df.to_csv('secrets.csv')

			name = request.form['name']
			num = request.form['num']
			email = request.form['email']
			password = request.form['password']
			age = request.form['age']
			gender = request.form['gender']

			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")			
			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (Date text,Name text,Contact text,Email text,password text,age text,gender text)")
			cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?,?,?)",(dt_string,name,num,email,password,age,gender))
			con.commit()

			return redirect(url_for('login'))

	return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	global video
	global name
	if request.method == 'POST':
		name = request.form['name']
		password = request.form['password']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT Name from Users WHERE Name='{name}' AND password = '{password}';")

	
		if(cursorObj.fetchone()):
			return redirect(url_for('input'))
		else:
			error = "Invalid Credentials Please try again..!!!"
	return render_template('login.html',error=error)


@app.route('/input', methods=['GET', 'POST'])
def input():
	if request.method == 'POST':
		name = request.form["name"]
		email = request.form["email"]
		num = request.form["num"]
		age = request.form["age"]
		symptoms = request.form["symptoms"]

   
		
		utils.export("data/"+name+"-symptoms.txt", symptoms, "w")
				
		data = utils.getTrainData()

		def get_words_in_tweets(tweets):	
			all_words = []
			for (words, sentiment) in tweets:
	  			all_words.extend(words)
			return all_words

		def get_word_features(wordlist):		
		
			wordlist = nltk.FreqDist(wordlist)
			word_features = wordlist.keys()
			return word_features

		word_features = get_word_features(get_words_in_tweets(data))		
		


		def extract_features(document):		
			document_words = set(document)
			features = {}
			for word in word_features:
				#features[word.decode("utf8")] = (word in document_words)
				features[word] = (word in document_words)
			#print(features)
			return features

		allsetlength = len(data)
		print(allsetlength)		
		#training_set = nltk.classify.apply_features(extract_features, data[:allsetlength/10*8])		
		training_set = nltk.classify.apply_features(extract_features, data[:88])
		#test_set = data[allsetlength/10*8:]		
		test_set = data[88:]		
		classifier = nltk.NaiveBayesClassifier.train(training_set)			
		
		def classify(symptoms):
			return(classifier.classify(extract_features(symptoms.split())))
			
				
			
		f = open("data/"+ name+"-symptoms.txt", "r")	
			
		#print(tot,neg,pos)
		for symptoms in f:
			#tot = tot + 1
			result = classify(symptoms)

		return render_template('input.html',name=name,email=email,num=num,age=age,symptoms=symptoms,result=result)			    
	
	return render_template('input.html')

@app.route('/video', methods=['GET', 'POST'])
def video():
	return render_template('video.html')


@app.route('/video_stream')
def video_stream():
	new_ewq = 0
	return Response(get_frame(new_ewq),mimetype='multipart/x-mixed-replace; boundary=frame')

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__':# and run:
	app.run(host='0.0.0.0', debug=True, threaded=True)
	#app.run()