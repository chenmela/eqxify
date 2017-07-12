from flask import Flask, redirect, request, session
from bs4 import BeautifulSoup
import datetime as dt
import requests
from random import SystemRandom
from requests_oauthlib import OAuth2Session
import base64
import json

app = Flask(__name__)
client_id = "c5339f8e511445639d2bb229746c5576" 
client_secret = "24272a4c1671447d8adff36928c4975f" 
redirect_uri = "http://127.0.0.1:5000/callback"
scope = "playlist-modify-private"
token_url = "https://accounts.spotify.com/api/token"
authorize_url = "https://accounts.spotify.com/authorize"
base_url = "https://api.spotify.com"
user_id = "melaniechencp"

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
		day = day - dt.timedelta(days=1)

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
def spotify():
	response_type = "code"
	
	oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope)
	
	auth_url, state = oauth.authorization_url(url=authorize_url)
	session['oauth_state'] = state
	session.modified = True	
	return redirect(auth_url)

@app.route('/callback', methods=['GET'])
def callback():
	'''oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, state=session['oauth_state'])
	session['oauth_token'] = oauth.fetch_token(token_url=token_url, client_secret=client_secret, authorization_response=request.url)
	return redirect(url_for('.update'))
	'''
	auth_token = request.args['code']
	payload = {
		"grant_type": "authorization_code",
		"code": str(auth_token),
		"redirect_uri": redirect_uri
	}
	base64encoded = base64.b64encode("{}:{}".format(client_id, client_secret))
	header = {"Authorization": "Basic {}".format(base64encoded)}
	r = requests.post(token_url, data=payload, headers=header)
	response = json.loads(r.text)
	session["access_token"] = response["access_token"]
	session["refresh_token"] = response["refresh_token"]
	
	authorization_header = {
		"Authorization":
		"Bearer {}".format(session["access_token"]),
		"Content-Type": "application/json"
	}

	create_playlist_endpoint = "{}/v1/users/{}/playlists".format(base_url)
	
	create_playlist_response = requests.post(


@app.route('/update', methods=['GET'])
def update():
	oauth = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, scope=scope, token=session['oauth_token'])
	extra = {
		'client_id': client_id,
		'client_secret': client_secret,
	}
	session['oauth_token'] = oauth.refresh_token(token_url=token_url, **extra)
	return "hi"	


app.secret_key = "abc"
