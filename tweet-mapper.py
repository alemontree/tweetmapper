from flask import Flask, render_template
from flask.ext.socketio import SocketIO
import time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import urllib2
import logging
import config
import traceback

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.WARNING)
app = Flask(__name__, static_url_path='')
app.debug = False
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def home():
    return app.send_static_file('about.html')

@app.route('/tweetmapper')
def map():
    return app.send_static_file('index.html')


@socketio.on('message')
def handle_message(message):
    logging.info('message from client: %s', message)

@socketio.on_error()
def error_handler(e):
    logging.error('error: %s', e) 


class TweetListener(StreamListener):
    """Listens for tweets and sends users' locations via SocketIO
    """
    
    def __init__(self, socketio):
        super(TweetListener, self).__init__()
        self.socketio = socketio


    def on_data(self, data):
        try:
            parsed_data = json.loads(data)            
            coordinates = parsed_data["coordinates"]
            
            loc = parsed_data["user"]["location"]
            if not loc:
                return True             
            logging.info(loc)
            self.socketio.send(loc)
            return True
        except Exception as e:
            logging.error("Unexpected exception: %s", 
                traceback.format_exc())
            return True

    def on_exception(self, exception):
        logging.error("exception: %s", str(exception))


consumer_key="y6avwjoMCJ1NwBEUXRVlK3kNW"
consumer_secret="bGOTUWos8N2XkssW7KCSJxkuOJgH2s9oOgyoHLOLQeE5RquIFs"

access_token="22721579-VjNiIU7xErbaADurQdS6VIwlBeMi6SzUlIT4j5R7A"
access_token_secret="meHvXUBQWr3HLnTfVgkNPEXvzgtgJ8oyCmKPLYtaGKNVg"


if __name__ == "__main__":
    l = TweetListener(socketio)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    stream.filter(track=['#android'], async=True) # blocking

    socketio.run(app, host=config.host, port=config.port)
