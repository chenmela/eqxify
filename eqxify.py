from flask import Flask
from bs4 import BeautifulSoup
import datetime as dt
import requests
from random import SystemRandom
from requests_oauthlib import OAuth2Session

app = Flask(__name__)

def scrapeData():
	times = ['12:00am', '12:30am', '1:00am', '1:30am', '2:00am',
	'2:30am', '3:00am', '3:30am', '4:00am', '4:30am', '5:00am',
	'5:30am', '6:00am', '6:30am', '7:00am', '7:30am', '8:00am',
	'8:30am', '9:00am', '9:30am', '10:00am', '10:30am', '11:00am',
	'11:30am', '12:00pm', '12:30pm', '1:00pm', '1:30pm', '2:00pm',
	'2:30pm', '3:00pm', '3:30pm', '4:00pm', '4:30pm', '5:00pm',
	'5:30pm', '6:00pm', '6:30pm', '7:00pm', '7:30pm', '8:00pm',
	'8:30pm', '9:00pm', '9:30pm', '10:00pm', '10:30pm', '11:00pm',
	'11:30pm']

	day = dt.date.today()

	#Make requests for every 30-min interval in the past week
	for x in range(7):
		day = day - d
		t.timedelta(days=1)

		#Format date as MM/DD/YYYY
		date = day.strftime("%m/%d/%Y")
		
		#Get time from above list
		for time in times:

			payload = {'playlisttime': time, 'playlistdate': date, 
			'submitbtn': "Update"}
			
			r = requests.post("http://www.weqx.com/song-history/",
			data=payload)
			
			#Parse through text to get all songs from past week 
			bs = BeautifulSoup(r.text, "html.parser")
			songs = bs.find_all("div", class_="songhistoryitem")
			
			for s in songs:
				text = s["title"]
				song = text.split(" - ")[0]
				artist = text.split(" - ")[1]
@app.route('/')
def spotifyOAuth():
	clientID = ""
