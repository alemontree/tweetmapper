Tweet Mapper
==============

Maps tweets in realtime using users' locations on a Google Map.

The server runs Python with Flask. It consumes tweets via Twitter's Streaming API (using [Tweepy](https://github.com/tweepy/tweepy)) and sends them to the client using [SocketIO](https://github.com/miguelgrinberg/Flask-SocketIO).

The Javascript client listens for locations from the SocketIO server and geocodes them with the Google Maps API and then plots them on a Google Map.

