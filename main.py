from flask import Flask, render_template
from flask.ext.socketio import SocketIO
import time
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import urllib2
import threading

print("I AM GOING CRAZY x2 ")

app = Flask(__name__, static_url_path='')
app.debug = True
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

client_count = 0

@app.route('/')
def map():
    return app.send_static_file('index.html')


@socketio.on('message')
def handle_message(message):
    print 'message from client: ' + message

@socketio.on('client-connected')
def handle_message(message):
    print 'client-connected'
    client_count = client_count + 1

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



class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    
    def __init__(self, socketio):
        # super(StdOutListener, self).__init__()
        self.socketio = socketio
        print("THIS IS GETTING PRINTED TWICE")


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

            #loc = loc.encode('ascii', 'ignore')
            #loc = urllib2.quote(loc)

            print(loc, threading.current_thread())
            self.socketio.send(loc)



            #self.socketio.send('{{"lat":{},"lng":{}}}'.format(lat, lng), json=True)

            # url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % loc
            # print(url)
            # response = urllib2.urlopen(url)
            # geocode_json = response.read()
            # parsed_geodata = json.loads(geocode_json)
            # if len(parsed_geodata["results"]) == 0:
            #     return True




            # lat = parsed_geodata["results"][0]["geometry"]["location"]["lat"]
            # lng = parsed_geodata["results"][0]["geometry"]["location"]["lng"]
            # print(lat, lng)

            # self.socketio.send('{{"lat":{},"lng":{}}}'.format(lat, lng), json=True)

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
    print("I AM GOING CRAZY")
    l = StdOutListener(socketio)
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    stream = Stream(auth, l)
    t = threading.Thread(target=start_stream, args=(stream,))
    t.daemon = True

    t.start()


    socketio.run(app) # blocking
