"""This program is a simple streamer which read in 
only real-time tweets and stores then in a database"""

import tweepy
import json
from pymongo import MongoClient
from datetime import datetime
import time
import sys
import emoji
import re
import wget

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
collection = db['streamer'] 


def strip_emoji(text):
    new_text = re.sub(emoji.get_emoji_regexp(), r"", text)
    return new_text

def cleanList(text):
    text = strip_emoji(text)
    text.encode("ascii", errors="ignore").decode()
    return text

#Processes the tweet to a dictionary which can be stored in the database collection
def processTweets(tweet):

    place_countrycode  =None
    place_name  =None
    place_country =None
    place_coordinates =None
    source =None
    exactcoord =None
    place=None
    tweetType="normal" #Sets tweet type as normal and if it doesn't change later it is a normal tweet
    try:
        created = tweet['created_at']
        tweet_id = tweet['id_str']  # The Tweet ID from Twitter in string format
        username = tweet['user']['screen_name']  # The username of the Tweet author
        verified = tweet['user']['verified']
        text = tweet['text']  # The entire body of the Tweet

        #Downloads the media from tweet 
        if "media" in tweet["entities"]:
            medias = tweet["entities"]["media"]
            #one tweet can have multiple images, so have to loop through
            for media in medias:
              wget.download(media["media_url"], 'crawlerMedia') #Stores media in "crawlerMedia" folder
    
    except Exception as e:
        return None

    try:
        #Checks to see if the tweet is extended or not
        if tweet['truncated']:
            text = tweet['extended_tweet']['full_text']

        elif text.startswith('RT'):
            tweetType = "retweet" #Sets tweet type in order to analyse types of tweet later
            try:
                if tweet['retweeted_status']['truncated']:
                    text = tweet['retweeted_status']['extended_tweet']['full_text']   
                else:
                    text = tweet['retweeted_status']['full_text']

            except Exception as e:
                pass

        #Used to check if the tweet is a quote in order to analyse types of tweet later
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
    
    #Puts tweet info in dictionary to store in collection
    tweet = {'_id' : tweet_id, 'type': tweetType, 'date': created, 'verified': verified, 'username': username,  'text' : text,  'geoenabled' : geoenabled,  'coordinates' : coordinates,  'location' : location,  'place_name' : place_name, 'place_country' : place_country, 'country_code': place_countrycode,  'place_coordinates' : place_coordinates, 'hashtags' : hList, 'mentions' : mList, 'source' : source}

    return tweet


class StreamListener(tweepy.StreamListener):

    def on_connect(self):ç
        print("You are now connected to the streaming API.")

    def on_error(self, status_code):
        print('An Error has occured: ' + repr(status_code))
        return False

    def on_data(self, data):
        t = json.loads(data)
        tweet = processTweets(t)
        try:
            collection.insert_one(tweet)
        except Exception as e:
            print(e)
        
# Coordinates for UK and Ireland
Loc_UK = [-10.392627, 49.681847, 1.055039, 61.122019] 

#Words wanting to be searched for in steamer
Words_UK =["Rangers", "Foul", "Gers", "Red Card", "Ref", "Referee" "Europa League", "Slavia Praha", "Football", "Offside", "Goal", "VAR", "Morelos", "Ryan Kent", "#RANSLA", "Hagi", "Save", "McGregor", "#RFC", "Gerrard", "Freekick", "Penalty", "Man United", "AC Milan", "#ACMMUFV", "#UEL", "#MUFC" "Zlatan", "Rashford", "Fernandes", "Martial", "Pogba", "Milan", "Maguire"]

print("Tracking: " + str(Words_UK))
listener = StreamListener(api=tweepy.API(wait_on_rate_limit=True))
streamer = tweepy.Stream(auth=auth, listener=listener)

#Takes live tweets and only accounts for ones in the UK or the ones that match the defined words
streamer.filter(locations= Loc_UK, track = Words_UK, languages = ['en'], is_async=True)


