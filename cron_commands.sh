#!/bin/bash
export FLASK_APP=eqxify.py
flask run&

while ! nc -z localhost 5000; do
	sleep 0.1
done
firefox 127.0.0.1:5000/add_songs &
