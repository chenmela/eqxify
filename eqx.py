from bs4 import BeautifulSoup
import requests
import datetime as dt
import collections

NUM_HITS = 26

'''
Scrapes data from 102.7 WEQX song history log, finds the top NUM_HITS hits
for the day

Params: None

Returns a list of NUM_HITS dictionaries, each of which contains 1) artist
and 2) song title
'''

def scrape_data():
    #Create list to hold top hits
    top_hits = []
    
    #Create list to hold artist and song title of each song history log record
    songs_and_artists = []

    #Create list of times to query song history log
    times = ['12:00am', '12:30am', '1:00am', '1:30am', '2:00am',
    '2:30am', '3:00am', '3:30am', '4:00am', '4:30am', '5:00am',
    '5:30am', '6:00am', '6:30am', '7:00am', '7:30am', '8:00am',
    '8:30am', '9:00am', '9:30am', '10:00am', '10:30am', '11:00am',
    '11:30am', '12:00pm', '12:30pm', '1:00pm', '1:30pm', '2:00pm',
    '2:30pm', '3:00pm', '3:30pm', '4:00pm', '4:30pm', '5:00pm',
    '5:30pm', '6:00pm', '6:30pm', '7:00pm', '7:30pm', '8:00pm',
    '8:30pm', '9:00pm', '9:30pm', '10:00pm', '10:30pm', '11:00pm',
    '11:30pm']

    #Get every 30-min interval in the past day
    day = dt.date.today() - dt.timedelta(days=1)

    #Format date as MM/DD/YYYY
    date = day.strftime("%m/%d/%Y")
            
    #Get time from above list
    for time in times:

        #Create payload for making request to WEQX webpage
        payload = {'playlisttime': time, 'playlistdate': date, 
        'submitbtn': "Update"}
        
        #Make the request
        r = requests.post("http://www.weqx.com/song-history/",
        data=payload)
                    
        #Parse through text to get all songs from this time interval 
        bs = BeautifulSoup(r.text, "html.parser")
        eqx_songs = bs.find_all("div", class_="songhistoryitem")
    
        for s in eqx_songs:
            try:
                text = s["title"].encode("utf-8")
                artist = text.split(" - ")[0]
                song = text.split(" - ")[1]
                songs_and_artists.append((song, artist))
            except:
                continue

    #Use counter module to calculate most common hits of the day
    counter = collections.Counter(songs_and_artists)
    for song_and_artist, count in counter.most_common(NUM_HITS+1):

        #Add most popular NUM_HITS songs and artists to the list of top hits    
        top_hits.append([song_and_artist[0], song_and_artist[1]])
    return top_hits
