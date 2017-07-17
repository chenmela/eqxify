#import statements
from flask import Flask, redirect, request
import urllib #Used for creating params section of request url
import base64
import requests
import json

#Flask app syntax
app = Flask(__name__)

#Global variables
client_id = ""
client_secret = ""
auth_url = "https://accounts.spotify.com/authorize"
redirect_uri = "http://127.0.0.1:5000/callback"		
scope = "playlist-modify-private"
show_dialog = True
response_type = "code"
grant_type = "authorization_code"
access_token_url = "https://accounts.spotify.com/api/token"
username = "melaniechencp"
content_type = "application/json"
playlist_name = "Created by eqxify"

auth_request_params = {
	"client_id": client_id, 
	"response_type": response_type,
	"redirect_uri": redirect_uri,
	"show_dialog": str(show_dialog).lower()
}

#Helper function to generate random state
def get_random_state():
	possible = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	text = []
	
	#SystemRandom() implements os.urandom() which is 
	#crytographically secure
	randomGen = SystemRandom()

	for x in range(16):
		text.append(randomGen.choice(possible))

	state = "".join(text)
	return state

#Spotify Authorization Code Flow at https://developer.spotify.com/web-api/authorization-guide/#authorization_code_flow

@app.route("/")
def home():
	#Step 1: App requests authorization to access user data
	#When control reaches this route, we redirect to a 
	#Spotify authorization page (specified by auth request url)
	
	#.join() joins all elements of a sequence with the
	#specified string
	auth_request_args = "&".join(["{}={}".format(key,urllib.quote(value)) for key, value in auth_request_params.iteritems()])
	auth_request_url = "{}/?{}".format(auth_url, auth_request_args)
	#Essentially a GET request
	return redirect(auth_request_url)

#Step 2: Occurs outside our app. The user is asked to authorize
#access within the specified scopes.

#Step 3: Also occurs outside our app. The user is redirected back
#to the redirect_uri supplied in the parameters of our request.

@app.route("/callback")
def callback():
	#Step 4: Our application requests refresh and access tokens
	#We use request.args to get this info because the spotify
	#client made a request to our server.
	auth_code = request.args["code"]
	#TODO: figure out state security
	#state = request.args["state"]
	access_params = {
		"grant_type": grant_type,
		"code": str(auth_code),
		"redirect_uri": redirect_uri	
	}
	
	access_header_vals = base64.b64encode("{}:{}".format(
	client_id, client_secret))
	access_headers = {"Authorization": "Basic {}".format(
	access_header_vals)}
	
	#A POST request
	access_request = requests.post(access_token_url,
	data = access_params, headers=access_headers)
	
	#Step 5: Tokens are returned to our application.
	#We use json.loads to get this info because we made the
	#request to the spotify server.
	access_response = json.loads(access_request.text)
	access_token = access_response["access_token"]
	token_type = access_response["token_type"]
	expires_in = access_response["expires_in"]
	refresh_token = access_response["refresh_token"]
	
	#Step 6: Use the access token to access the Spotify Web API
	#Specifically, we will create a playlist.

	#TODO: Make username variable and specific to user
	
	create_playlist_endpoint = "https://api.spotify.com/v1/users/{}/playlists".format(username)

	create_playlist_headers = {
		"Authorization": session["access_token"],
		"Content-Type": content_type
	}
	
	create_playlist_response = requests.post(
	create_playlist_endpoint, data=create_playlist_params,
	headers=create_playlist_headers, json = {"name": name})
 
app.secret_key = "abc"
