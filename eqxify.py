#import statements
from flask import Flask, redirect, request, url_for, session
import urllib #Used for creating params section of request url
import base64
import requests
import json
import eqx
import io

#Flask app syntax
app = Flask(__name__)

#Global variables
client_id = ""
client_secret = ""
auth_url = "https://accounts.spotify.com/authorize"
app_uri = "http://127.0.0.1:5000/"
redirect_uri = "http://127.0.0.1:5000/callback"		
scope = "playlist-modify-private playlist-modify-public"
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
	"scope": scope,
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
	
	#Check to see if error has occurred
	if ("code" not in request.args):
		return "You have not authorized access to eqxify. Revisit {} to try again.".format(app_uri)

	auth_code = request.args["code"]
		
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
	data=access_params, headers=access_headers)
	
	#Step 5: Tokens are returned to our application.
	#We use json.loads to get this info because we made the
	#request to the spotify server.
	access_response = json.loads(access_request.text)
	
	#If first time obtaining access_token, write to a file
	if ("access_token" in access_response):
		access_token = access_response["access_token"]
		token_type = access_response["token_type"]
		scope = access_response["scope"]
		expires_in = access_response["expires_in"]
		refresh_token = access_response["refresh_token"]
		
		#Write access token, refresh token and metadata to a file
		token_dict = {
			"access_token" : access_token,
			"token_type" : token_type,
			"expires_in" : expires_in,
			"refresh_token" : refresh_token
		}
		iostream = open("tokens.txt", 'w')
		json.dump(token_dict, iostream)
		iostream.close()

		#Save access token for different function calls within the same session
		session["access_token"] = access_token
	else:
		redirect(url_for("refresh"))
	
	return redirect(url_for("add_songs"))
	
@app.route("/refresh")
def refresh():
	#Open stored values of access_token if unable to request it
	iostream = open("tokens.txt", 'r')
	token_dict = json.load(iostream)

	#Step 6: Request access token from refresh token
	refresh_params = {
		"grant_type": "refresh_token",
		"refresh_token" : token_dict["refresh_token"]
	}

	#Create headers and make request for refresh token
	refresh_header_vals = base64.b64encode("{}:{}".format(
	client_id, client_secret))
	refresh_headers = {"Authorization": "Basic {}".format(
	refresh_header_vals)}
	
	refresh_token_url = access_token_url
	refresh_request = requests.post(refresh_token_url,
	data=refresh_params, headers=refresh_headers)
	
	refresh_response = json.loads(refresh_request.text)
	if ("access_token" not in refresh_response):
		return "Token could not be obtained and/or refreshed."

 	#If refresh request was successful, update session access_token and file
	session["access_token"] = refresh_response["access_token"]
	iostream.close()
	
	token_dict = {
		"access_token" : refresh_response["access_token"],
		"token_type" : refresh_response["token_type"],
		"scope" : refresh_response["scope"],
		"expires_in" : refresh_response["expires_in"]
	}
	iostream = open("tokens.txt", 'w')
	json.dump(token_dict, iostream)
	iostream.close()	

@app.route("/add_songs")
def add_songs():
	#Step 7: Get data from EQX website	
	#scraper = eqx.EQXDataScraper()
	#scraper.scrape_data()

	#Step 8: Use the access token to access the Spotify Web API
	#Specifically, we will create a playlist and add songs.

	create_playlist_endpoint = "https://api.spotify.com/v1/users/{}/playlists".format(username)
	create_playlist_headers = {
		"Authorization": "Bearer {}".format(session["access_token"]),
		"Content-Type": content_type
	}
	create_playlist_payload = {
		"name": "hello"
	}	
	create_playlist_request = requests.post(
	create_playlist_endpoint, headers=create_playlist_headers,
	json=create_playlist_payload)
	create_playlist_response = json.loads(create_playlist_request.text)
	return create_playlist_request.content
	
if __name__ == '__main__':    	
	app.run(debug=True)

app.secret_key = "abc"
