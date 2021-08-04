# Python Twitter API Crawler

This project was to use the Twitter streaming api to read in real-time text (see crawler.py). Then this data was run through a clustering file to put the tweets into groups based on similarity and the identifies 10 keys words for each cluster (see cluster.py). The key words were then supposed to be run through a Hybrid API which combined the streaming API and a new search API which can gather pre-existing tweets. This means more data is being collected as the key words, identified in cluster.py, are identifying tweets which are being tweeted in real time and pre-existing ones (see hybridCrawler.py).
 

### Installing Dependencies


This was used to interact with the Twitter API:
```
pip install tweepy
```

This was used to save tweets to a local database:
```
pip install pymongo
```

This was used to put the Tweets into dataframes in order to make the processing easier
```
pip install pandas
```

This was used to calculate the key words in each cluster
```
pip install numpy
```

This was used to download the media files from the url
```
pip install wget
```


This was used to identify and group tweets into clusters
```
pip install Scikit-learn
```

### Running

- Streamer Crawler - Add your Twitter Developer keys and run the following when you have the folder active in the console:
```
python crawler.py
```

  
- Clustering Streamer Tweets - Run the following when you have the folder active in the console and you have already run the streamer:
```
python cluster.py
```

- Hybrid Crawler - Add your Twitter Developer keys and run the following when you have the folder active in the console:
```
python hybridCrawler.py
```

- Mongo Query (provides analyse on the Tweets collected from the Streamer and Hybrid Crawler)- Run the following when you have the folder active in the console:
```
python hybridCrawler.py
```



## Acknowledgments

- [Tweepy Documentation](http://docs.tweepy.org/en/latest/)
- [Twitter Developer Documentation](https://developer.twitter.com/en/docs)
- [How I clustered the tweets](https://stackoverflow.com/questions/27889873/clustering-text-documents-using-scikit-learn-kmeans-in-python?fbclid=IwAR13agTGUdH3e7Xdpt2x6ee6R8vrzjWCuguWgCgTklOcmcYBwVdO6ak8c3k)


