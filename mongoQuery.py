"""This file carries out analysis on the collections to obtain data which was necessary for the coursework report"""

from pymongo import MongoClient

client = MongoClient('localhost',27017)  
db = client["TwitterDump"]
#Reads in the Streamer collection, collected from "crawler.py"
streamer = db['streamer'] 

#Reads in the Streamer collection, collected from hybridCrawler
hybridStreamer = db['hybridStreamer'] 

#Reads in the search API collection, collected from hybridCrawler
hybridAPI=db['hybridSearch']

#Displays the analysed data for the streamer
print("")
print("")
print("----------------------------")
print("STREAMER TWEET DATA ANALYSED")
print("----------------------------")
print("Total number of total tweets from streamer: " + str(streamer.count_documents(filter={})))
print("Total number of normal tweets: " + str(streamer.count_documents(filter={'type':'normal'})))
print("Total number of quote tweets: " + str(streamer.count_documents(filter={'type':'quote'})))
print("Total number of retweets: " + str(streamer.count_documents(filter={'type':'retweet'})))
print("")
print("Total number of Geo Tagged tweets: " + str(streamer.count_documents(filter={'geoenabled':True})))
print("Total number of GPS Geo Tagged tweets: " + str(streamer.count_documents(filter={'coordinates': {'$ne':None}})))
print("Total number of Generic Location tweets: " + str(streamer.count_documents(filter={'location': {'$ne':None}})))
print("Total number of Twitter Place tweets: " + str(streamer.count_documents(filter={'place_name': {'$ne':None}})))
print("Total number of Verified users: " + str(streamer.count_documents(filter={'verified':True})))
print("")
print("")

totalRedundant = 0
redundantQuotes = 0
redundantRetweets = 0
redundantNormal=0

#Counts the amount redundant data between the two Hybrid collections and calculates the number of redundant data for each type of tweet
for tweet in hybridAPI.find():
    redundant = hybridStreamer.count_documents(filter={'_id': tweet["_id"]})
    if redundant == 1:
        totalRedundant += 1
        if hybridAPI.find_one(filter={'_id': tweet["_id"]})["type"]  == "quote":
            redundantQuotes += 1
        elif hybridAPI.find_one(filter={'_id': tweet["_id"]})["type"] == "retweet":
            redundantRetweets += 1
        else:
            redundantNormal += 1

#Displays the analysed data for the Hybrid streamer/search API
print("---------------------------------------")
print("HYBRID API/STREAMER TWEET DATA ANALYSED")
print("---------------------------------------")
print("Total tweets for both streamers (including redundant data): " + str(hybridStreamer.count_documents(filter={}) + hybridAPI.count_documents(filter={})))
print("Total tweets for both streamers (excluding redundant data): " + str(hybridStreamer.count_documents(filter={}) + hybridAPI.count_documents(filter={})- totalRedundant))
print("Total tweets for hybrid streamer: " + str(hybridStreamer.count_documents(filter={})))
print("Total tweets for hybrid search API: " + str(hybridAPI.count_documents(filter={})))
print("")
print("Total number of redundant: " + str(totalRedundant))
print("Total number of redundant retweets: " + str(redundantRetweets))
print("Total number of redundant quotes: " + str(redundantQuotes))
print("Total number of redundant normal tweets: " + str(redundantNormal))
print("")
print("Total number of quotes (including duplicate data): " + str(hybridStreamer.count_documents(filter={'type':'quote'}) + hybridAPI.count_documents(filter={'type':'quote'})))
print("Total number of normal tweets (including duplicate data): " + str(hybridStreamer.count_documents(filter={'type':'normal'}) + hybridAPI.count_documents(filter={'type':'normal'})))
print("Total number of retweets (including duplicate data): " + str(hybridStreamer.count_documents(filter={'type':'retweet'}) + hybridAPI.count_documents(filter={'type':'retweet'})))
print("")
print("Total number of quotes (not including duplicate data): " + str(hybridStreamer.count_documents(filter={'type':'quote'}) + hybridAPI.count_documents(filter={'type':'quote'}) - redundantQuotes))
print("Total number of normal tweets (not including duplicate data): " + str(hybridStreamer.count_documents(filter={'type':'normal'}) + hybridAPI.count_documents(filter={'type':'normal'}) - redundantNormal))
print("Total number of retweets (not including duplicate data): " + str(hybridStreamer.count_documents(filter={'type':'retweet'}) + hybridAPI.count_documents(filter={'type':'retweet'}) - redundantRetweets))
print("")
print("Total number of Geo Tagged tweets: " + str(hybridStreamer.count_documents(filter={'geoenabled':True}) + hybridAPI.count_documents(filter={'geoenabled':True})))
print("Total number of GPS Geo Tagged tweets: " + str(hybridStreamer.count_documents(filter={'coordinates': {'$ne':None}}) + hybridAPI.count_documents(filter={'coordinates': {'$ne':None}})))
print("Total number of Generic Location tweets: " + str(hybridStreamer.count_documents(filter={'location': {'$ne':None}}) + hybridAPI.count_documents(filter={'location': {'$ne':None}})))
print("Total number of Twitter Place tweets: " + str(hybridStreamer.count_documents(filter={'place_name': {'$ne':None}}) + hybridAPI.count_documents(filter={'place_name': {'$ne':None}})))
print("Total number of Verified users: " + str(hybridStreamer.count_documents(filter={'verified':True}) + hybridAPI.count_documents(filter={'verified':True})))