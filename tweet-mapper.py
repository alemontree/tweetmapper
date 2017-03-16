from flask import Flask, render_template
from flask_socketio import SocketIO
import time
from keys import secrets
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
# import urllib2
# import urllib3
import logging
import config
import traceback

# urllib3.disable_warnings()
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

@app.route('/robots.txt')
def robot():
    return app.send_static_file('robots.txt')

@socketio.on('message')
def handle_message(message):
    logging.info('message from client: {}'.format(message))

@socketio.on_error()
def error_handler(e):
    logging.error('error: {}'.format(e)) 


class TweetListener(StreamListener):
    """Listens for tweets and sends users' locations via SocketIO
    """
    
    def __init__(self, socketio):
        super(TweetListener, self).__init__()
        self.socketio = socketio


    def on_data(self, data):
        try:
            parsed_data = json.loads(data)
                       
            #coordinates = parsed_data["coordinates"]
            if not "user" in parsed_data:
                logging.warning("USER KEY MISSING\n", parsed_data)
                return True
            loc = parsed_data["user"]["location"]
            if not loc:
                #logging.warning(parsed_data) 
                return True             
            logging.info(loc)
            self.socketio.send(loc)
            return True
        except Exception as e:
            logging.error('Unexpected exception: {}'.format(traceback.format_exc(e)))
            return True

    def on_timeout(self):
        logging.warning("Timeout Occured")
        return

    def on_disconnect(self, notice):
        """Called when twitter sends a disconnect notice
        Disconnect codes are listed here:
        https://dev.twitter.com/docs/streaming-apis/messages#Disconnect_messages_disconnect
        """
        logging.warning("disconnect: {}".format(notice))
        return True

    def on_exception(self, exception):
        logging.error("Exception: {}".format(str(exception)))
        return True

    def on_error(self, status_code):
        logging.error("Error code {}".format(status_code))
        if status_code == 420:
            #returning False in on_error disconnects the stream
            return False

        # returning non-False reconnects the stream, with backoff.
        return True





if __name__ == "__main__":
    l = TweetListener(socketio)
    auth = OAuthHandler(secrets['consumer_key'], secrets['consumer_secret'])
    auth.set_access_token(secrets['access_token'], secrets['access_token_secret'])
    stream = Stream(auth, l)
    stream.filter(track=['#BlackLivesMatter'], async=True, stall_warnings=True) # blocking    

    # while True: 
    #     try:
    #         stream = Stream(auth, l)
    #         stream.filter(track=['#BlackLivesMatter'], async=True, stall_warnings=True) # blocking
    #     except:
    #         continue
    print ("app running on port {}".format(config.port))
    socketio.run(app, host=config.host, port=config.port)

    # try: 
    #     socketio.run(app, host=config.host, port=config.port)
    # except KeyboardInterrupt:
    #     logging.error("Keyboard Interrupt")
        
