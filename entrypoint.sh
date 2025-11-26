#!/bin/sh

# Start the Flask app
# Using gunicorn for better stability, but flask run is also fine for CTF
# 1 worker is enough for a CTF challenge usually, but we can do 4
exec gunicorn --bind 0.0.0.0:5000 app:app
