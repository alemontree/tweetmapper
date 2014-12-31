from __future__ import absolute_import, print_function

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import json
import urllib2

# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after
consumer_key="y6avwjoMCJ1NwBEUXRVlK3kNW"
consumer_secret="bGOTUWos8N2XkssW7KCSJxkuOJgH2s9oOgyoHLOLQeE5RquIFs"

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section
access_token="22721579-VjNiIU7xErbaADurQdS6VIwlBeMi6SzUlIT4j5R7A"
access_token_secret="meHvXUBQWr3HLnTfVgkNPEXvzgtgJ8oyCmKPLYtaGKNVg"

class StdOutListener(StreamListener):
    """ A listener handles tweets are the received from the stream.
    This is a basic listener that just prints received tweets to stdout.
    """
    def on_data(self, data):
        # print(data)
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
            loc = urllib2.quote(loc)
            url = "https://maps.googleapis.com/maps/api/geocode/json?address=%s" % loc
            print(url)
            response = urllib2.urlopen(url)
            geocode_json = response.read()
            parsed_geodata = json.loads(geocode_json)
            
            #print(parsed_geodata["results"])
            lat = parsed_geodata["results"][0]["geometry"]["location"]["lat"]
            lng = parsed_geodata["results"][0]["geometry"]["location"]["lng"]
            print(lat, lng)


        


        return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    l = StdOutListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(track=['NYPD'])
 