from flask import Flask, render_template
from flask.ext.socketio import SocketIO
import time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import urllib2
import threading

app = Flask(__name__, static_url_path='')
app.debug = False
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def map():
    return app.send_static_file('index.html')


@socketio.on('message')
def handle_message(message):
    print 'message from client: ' + message

@app.route('/bcast')
def broadcast():
    print 'broadcasting'
    socketio.emit('test', 'this is the server speaking ' + str(time.time()))
    socketio.send('asdf')
    return "broadcasted"

@app.route('/map')
def send_marker():
    socketio.send('{"lat":35,"lng":-120}', json=True)
    return "mapped"

@socketio.on_error()
def error_handler(e):
    print 'error: ' + e



class TweetListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    
    def __init__(self, socketio):
        super(TweetListener, self).__init__()
        self.socketio = socketio


    def on_data(self, data):
        parsed_data = json.loads(data)
        
        coordinates = parsed_data["coordinates"]
        if coordinates:
            print(parsed_data["text"])
            print(parsed_data["user"]["name"])
            print(parsed_data["coordinates"])
            print()
        else:
            loc = parsed_data["user"]["location"]
            if not loc:
                return True             
            print(loc)
            self.socketio.send(loc)
        return True

    def on_exception(self, exception):
        print("exception: " + str(exception))



consumer_key="y6avwjoMCJ1NwBEUXRVlK3kNW"
consumer_secret="bGOTUWos8N2XkssW7KCSJxkuOJgH2s9oOgyoHLOLQeE5RquIFs"

access_token="22721579-VjNiIU7xErbaADurQdS6VIwlBeMi6SzUlIT4j5R7A"
access_token_secret="meHvXUBQWr3HLnTfVgkNPEXvzgtgJ8oyCmKPLYtaGKNVg"

  



def start_stream(stream):
    stream.filter(track=['Buckeyes']) # blocking
    # stream.filter(track=['NYPD'])

if __name__ == "__main__":
    l = TweetListener(socketio)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    t = threading.Thread(target=start_stream, args=(stream,))
    t.daemon = True

    t.start()


    socketio.run(app)