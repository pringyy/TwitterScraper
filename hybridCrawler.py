"""This program is a hybrid between a streamer which reads in 
real-time tweets and a search API which reads in pre-exisiting tweets """

import tweepy
import wget
import json
from pymongo import MongoClient
from datetime import datetime
import time
import sys
import emoji
import re

#Enter your Tiwtter API  developer details here
consumer_key = "jLMx846va7gEO5qcGQunWS02x"
consumer_secret ="WmGNYKHsc7xqoAvWffC3AKQ984RxByqFwHqDWQrnvOs8Zqs23w"
access_token ="1067428438724640769-LwZdgrc7VA9Qt2jw92v7Uaz4TKKbVi"
access_token_secret ="09HYSmcZZslD8kFoEQtCJNVi2KxOSAnAptaokBWya2X3r"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret )
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

#This sets up a local MongoDB datbase
client = MongoClient('localhost',27017) 
db = client["TwitterDump"]
streamerDB = db['hybridStreamer'] #This will store data from the streamer in the Hybrid
searchDB=db['hybridSearch']  #This will store data from the search API in the hybrid


def strip_emoji(text):
    new_text = re.sub(emoji.get_emoji_regexp(), r"", text)
    return new_text

def cleanList(text):
    text = strip_emoji(text)
    text.encode("ascii", errors="ignore").decode()
    return text

#Processes the tweet to a dictionary which can be stored in the database collection
#Passes in method as the streamer and search api store text differently
def processTweets(tweet, method):

    place_countrycode  =None
    place_name  =None
    place_country =None
    place_coordinates =None
    source =None
    exactcoord =None
    place=None
    tweetType="normal"
    
    try:
        tweet_id = tweet['id_str']  # The Tweet ID from Twitter in string format
        username = tweet['user']['screen_name']  # The username of the Tweet author
        verified = tweet['user']['verified']

         #Downloads the media from tweet 
        if "media" in tweet["entities"]:
            medias = tweet["entities"]["media"]
             #one tweet can have multiple images, so have to loop through
            for media in medias:
              wget.download(media["media_url"], 'hybridMedia') #Stores media in "hybridMedia" folder

        #Check if it is a search or streamer tweet as text is stored differently for each
        if method == "search":
            text = tweet['full_text']  #The entire body of the Tweet  
        else:
            text=tweet["text"]

    except Exception as e:
        return None

    try:
        if tweet['truncated']:
            text = tweet['extended_tweet']['full_text']

        elif text.startswith('RT'):
            tweetType = "retweet"
            try:
                if tweet['retweeted_status']['truncated']:
                    text = tweet['retweeted_status']['extended_tweet']['full_text']   
                else:
                    text = tweet['retweeted_status']['full_text']

            except Exception as e:
                pass

        if tweet['is_quote_status']:
            tweetType = "quote"
    
        
    except Exception as e:
        pass

    text = cleanList(text)
    entities = tweet['entities']
    mentions =entities['user_mentions']
    mList = []

    for x in mentions:
        mList.append(x['screen_name'])
    hashtags = entities['hashtags']  # Any hashtags used in the Tweet
    hList =[]

    for x in hashtags:
        hList.append(x['text'])

    source = tweet['source']

    exactcoord = tweet['coordinates']
    coordinates = None

    if(exactcoord):
        coordinates = exactcoord['coordinates']
    
    geoenabled = tweet['user']['geo_enabled']
    location = tweet['user']['location']


    if geoenabled and text.startswith('RT') == False:
        
        try:
            if tweet['place']:
                place_name = tweet['place']['full_name']
                place_country = tweet['place']['country']
                place_countrycode   = tweet['place']['country_code']
                place_coordinates   = tweet['place']['bounding_box']['coordinates']

        except Exception as e:
            print(e)
            print('error from place details - maybe AttributeError: ... NoneType ... object has no attribute ..full_name ...')
    
    tweet = {'_id' : tweet_id, 'type': tweetType, 'verified': verified, 'username': username,  'text' : text,  'geoenabled' : geoenabled,  'coordinates' : coordinates,  'location' : location,  'place_name' : place_name, 'place_country' : place_country, 'country_code': place_countrycode,  'place_coordinates' : place_coordinates, 'hashtags' : hList, 'mentions' : mList, 'source' : source}
    return tweet

#All code until line 160 handles the streamer
class StreamListener(tweepy.StreamListener):

    def on_connect(self):
        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        return False

    def on_data(self, data):
        t = json.loads(data)
        tweet = processTweets(t, "streamer") #Pass in "streamer" as text object is stored differently between the streamer and search so has to be accounted for
        try:
            streamerDB.insert_one(tweet)
        except Exception as e:
           pass
        
Loc_UK = [-10.392627, 49.681847, 1.055039, 61.122019] # UK and Ireland
Words_UK =["goal", "uel", "spurs", "just", "mufc", "penalty", "milan", "manutd", "rangers", "time"]

print("Tracking: " + str(Words_UK))
listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=listener)
streamer.filter(locations= Loc_UK, track = Words_UK, languages = ['en'], is_async=True)

#Search API for rest of the file
Place =  'London'
Lat   =  '51.450798'
Long  =  '-0.137842'
geoTerm=Lat+','+Long+','+'10km'

last_id =  None
counter =0
sinceID = None
results = True
redundant = 0

while results:
    if (counter < 180):
        try:    
            #Searches the Twitter API for pre-existing tweets using the key workds and the location of the UK
            results = api.search(q = "goal OR uel OR spurs OR just OR mufc OR penalty OR milan OR manutd OR rangers OR time", geocode=geoTerm, count=100, lang="en", tweet_mode='extended')
            for tweet in results:
                t = json.loads(json.dumps(tweet._json))
                tweet = processTweets(t, "search") #Pass in "search" as text object is stored differently between the streamer and search so has to be accounted for
                if tweet != None:
                    try:
                        searchDB.insert_one(tweet) #inserts tweet into the search collection
                    except:
                        pass
                        
        except Exception as e:
            pass
        counter += 1
    else:
        time.sleep(15*60) #times out to account for Twitters 15 minute cool down using search API

