#import statements
from flask import Flask, redirect, request, url_for, session
import urllib #Used for creating params section of request url
import base64
import requests
import json
import eqx
import io
import os
from random import SystemRandom
#Flask app syntax
app = Flask(__name__)

#Global variables
AUTH_URL = "https://accounts.spotify.com/authorize"
APP_URI = "http://127.0.0.1:5000/"
REDIRECT_URI = "http://127.0.0.1:5000/auth"		
SCOPE = "playlist-modify-private playlist-modify-public"
SHOW_DIALOG = True
ACCESS_TOKEN_URL = "https://accounts.spotify.com/api/token"
CONTENT_TYPE = "application/json"
AUTH_REQUEST_PARAMS = {
	"client_id": CLIENT_ID, 
	"response_type": "code",
	"redirect_uri": REDIRECT_URI,
	"scope": SCOPE,
	"show_dialog": str(SHOW_DIALOG).lower()
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
	session["state"] = get_random_state()
	AUTH_REQUEST_PARAMS["state"] = session["state"]
	auth_request_args = "&".join(["{}={}".format(key,urllib.quote(value)) for key, value in AUTH_REQUEST_PARAMS.iteritems()])
	auth_request_url = "{}/?{}".format(AUTH_URL, auth_request_args)
	#Essentially a GET request
	return redirect(auth_request_url)

#Step 2: Occurs outside our app. The user is asked to authorize
#access within the specified scopes.

#Step 3: Also occurs outside our app. The user is redirected back
#to the redirect_uri supplied in the parameters of our request.

@app.route("/auth")
def auth():
	#Step 4: Our application requests refresh and access tokens
	#We use request.args to get this info because the spotify
	#client made a request to our server.
	
	#Check to see if error has occurred
	if ("code" not in request.args):
		return "You have not authorized access to eqxify. Revisit {} to try again.".format(APP_URI)
	#Check to see that request and repsonse originated in same browser
	if (request.args["state"] != session["state"]):
		return "State of request and response do not match. Revisit {} to try again.".format(APP_URI)

	auth_code = request.args["code"]
		
	access_params = {
		"grant_type": "authorization_code",
		"code": str(auth_code),
		"redirect_uri": REDIRECT_URI	
	}
	
	access_header_vals = base64.b64encode("{}:{}".format(
	CLIENT_ID, CLIENT_SECRET))
	access_headers = {"Authorization": "Basic {}".format(
	access_header_vals)}
	
	#A POST request
	access_request = requests.post(ACCESS_TOKEN_URL,
	data=access_params, headers=access_headers)
	
	#Step 5: Tokens are returned to our application.
	#We use json.loads to get this info because we made the
	#request to the spotify server.
	access_response = json.loads(access_request.text)
	
	#If first time obtaining access_token, write to a file
	if ("access_token" in access_response):
		access_token = access_response["access_token"]
		token_type = access_response["token_type"]
		SCOPE = access_response["scope"]
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
		return redirect(url_for("refresh"))
	
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
	session["refresh_token"] = token_dict["refresh_token"]

	#Create headers and make request for refresh token
	refresh_header_vals = base64.b64encode("{}:{}".format(
	CLIENT_ID, CLIENT_SECRET))
	refresh_headers = {"Authorization": "Basic {}".format(
	refresh_header_vals)}
	
	refresh_token_url = ACCESS_TOKEN_URL
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
		"expires_in" : refresh_response["expires_in"],
		"refresh_token" : session["refresh_token"]
	}
	iostream = open("tokens.txt", 'w')
	json.dump(token_dict, iostream)
	iostream.close()
	return redirect(url_for("add_songs"))	

@app.route("/add_songs")
def add_songs():
	if ("access_token" not in session):
		return redirect(url_for("refresh"))	
	#Step 7: Use the access token and username to access the Spotify Web API
	#First, we get the username of user who granted access.
	get_user_endpoint = "https://api.spotify.com/v1/me"
	get_user_headers = {
		"Authorization": "Bearer {}".format(session["access_token"])
	}
	get_user_request = requests.get(get_user_endpoint, headers=get_user_headers)
	get_user_response = json.loads(get_user_request.text)
	if ("id" not in get_user_response):
		if ("get_user_failures" in session):
			return "User name could not be found."
		session["get_user_failures"] = True
		return redirect(url_for("refresh"))
	session["user_id"] = get_user_response["id"]
	
	#Step 8: Get data from EQX website	
	scraper = eqx.EQXDataScraper()
	scraper.scrape_data()

	for hit in scraper.top_hits:
		print(hit)	
	#Step 9: Get Spotify track IDs for every song added to the top 25 hits.
	search_track_id_headers = {
		"Authorization": "Bearer {}".format(session["access_token"])
	}
	track_ids = []
	for hit in scraper.top_hits:
		try:
			track_artist = [term.replace(" ", "%20") for term in hit]
			query_string_params = {
				"track" : track_artist[0],
				"artist" : track_artist[1]
			}
			query_string = "%20".join(["{}:{}".format(key, value) for key, value in query_string_params.iteritems()])
			search_track_id_endpoint = "https://api.spotify.com/v1/search?"
			search_track_id_params = {
				"q" : query_string,
				"type" : "track",
				"limit" : "1"
			}
			search_track_id_endpoint += "&".join(["{}={}".format(key, value) for key, value in search_track_id_params.iteritems()])
			search_track_id_request = requests.get(search_track_id_endpoint, headers=search_track_id_headers)
			search_track_id_response = json.loads(search_track_id_request.text)
			track_ids.append(search_track_id_response["tracks"]["items"][0]["uri"])
		except:
			continue
	#Step 10: Check for existence of a playlist called Top 102.7 EQX Hits
	#If it exists, a file with its playlist ID exists. Otherwise, this file does not exist.
	if (not os.path.isfile("playlist_id.txt")):
		#Step 11a: If not present, create a playlist
		create_playlist_endpoint = "https://api.spotify.com/v1/users/{}/playlists".format(session["user_id"])
		create_playlist_headers = {
			"Authorization": "Bearer {}".format(session["access_token"]),
			"Content-Type": CONTENT_TYPE
		}
		create_playlist_payload = {
			"name": "Top 102.7 EQX Hits"
		}
		
		create_playlist_request = requests.post(
		create_playlist_endpoint, headers=create_playlist_headers,
		json=create_playlist_payload)
		create_playlist_response = json.loads(create_playlist_request.text)
		session["playlist_id"] = create_playlist_response["id"]
		playlist_dict = {
			"playlist_id": session["playlist_id"]
		}
		iostream = open("playlist_id.txt", 'w')
		json.dump(playlist_dict, iostream)
		iostream.close()

		#Step 12: Add songs to playlist just created
		add_songs_endpoint = "https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(session["user_id"], session["playlist_id"])
		add_songs_headers = create_playlist_headers
		add_songs_payload = {
			"uris": track_ids
		}
		add_songs_request = requests.post(add_songs_endpoint, headers=add_songs_headers, json=add_songs_payload)
		add_songs_response = json.loads(add_songs_request.text)
		return str(add_songs_response)

	#Step 11b: If present, replace all songs in existing playlist with new songs
 	else:
		#Set session playlist id since it wasn't populated
		#during creation of the playlist.
		iostream = open("playlist_id.txt", 'r')
		playlist_dict = json.load(iostream)

		session["playlist_id"] = playlist_dict["playlist_id"]
		replace_tracks_endpoint = "https://api.spotify.com/v1/users/{}/playlists/{}/tracks".format(session["user_id"], session["playlist_id"])
		replace_tracks_headers = {
			"Authorization": "Bearer {}".format(session["access_token"]),
			"Content-Type": CONTENT_TYPE
		}
		replace_songs_payload = {
			"uris": track_ids
		}
		replace_tracks_request = requests.put(replace_tracks_endpoint, headers=replace_tracks_headers, json=replace_songs_payload)
		replace_tracks_response = json.loads(replace_tracks_request.text)
		return str(replace_tracks_response)
if __name__ == '__main__':    	
	app.run(debug=True)

app.secret_key = os.urandom(24)
