# EQXify

Scrapes data from 102.7 WEQX online song history log, calculates
top hits of the day, and updates a user's Spotify playlist.

## Tools & Technology
* Python [requests] (http://docs.python-requests.org/en/master/), [Beautiful Soup] (https://www.crummy.com/software/BeautifulSoup/bs4/doc/), [collections] (https://docs.python.org/2/library/collections.html)
* [Flask] (http://flask.pocoo.org/)
* [Spotify API] (https://developer.spotify.com/web-api/)
* [Crontab] (https://help.ubuntu.com/community/CronHowto)
* [virtualenv] (https://virtualenv.pypa.io/en/stable/) (optional)


## Getting Started
Currently this project is compatible with Unix systems.

Clone this repository:
```
git clone https://github.com/chenmela/eqxify.git
```

Optional: Create a virtualenv
```
pip install virtualenv
virtualenv <your_venv_name>
```

Optional: Use your virtualenv
```
source <your_venv_name>/bin/activate
```

Either within or outside virtualenv:
```
pip install Flask
pip install BeautifulSoup4
pip install request
```

Create a Spotify app:
* Follow the instructions [here] (https://developer.spotify.com/web-api/)
* Add your client ID and client secret to eqxify.py
* Add http://127.0.0.1:5000 as your redirect URI on the Spotify dashboard (or another port)

Crontab (daily updates):
More details coming soon. Check out cron\_commands.sh for basics.

Run your app:
export FLASK\_APP=eqxify.py
flask run

Visit 127.0.0.1:5000, authorize access to the app, and enjoy!

##TODO:
* Updates to cron installation
* script for developers that takes client ID and secret,
automates set-up of Flask app and cron
* website/app for non-developers that prompts user to log in to 
Spotify and does the rest behind the scenes
