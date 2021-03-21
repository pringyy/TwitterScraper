'''This files clusters together tweets based on how similar they are
and then prints how key words which are then used in the hybrid crawler'''

from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as stopWords
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from string import ascii_lowercase
import pandas as panda
from pymongo import MongoClient

#Sets up MongoDB collection to be read in
client = MongoClient('localhost',27017) #is assigned local port
db = client["TwitterDump"]
collection = db['streamer'] 

print("Clustering " + str(collection.count_documents(filter={})) + " tweets...")

#Reads in all the tweets and stores it in a dataframe which makes it more efficient dealing with large amounts of data
dataFrame = panda.DataFrame(collection.find(filter={}).limit(50000))

#Transforms text into feature vectors which can be used as an input estimator to group similar tweets
vector = TfidfVectorizer(stop_words=stopWords.union(['rt', 'https', 'http', 've', 'don', 'won', 'll', 're']))
vector.fit(dataFrame['text'])
text = vector.transform(dataFrame['text'])

#Defines the a total of 10 clusters or groups that the tweets will be grouped into
numberOfClusters = 10

#Clusters tweets into similar groups
clusters = KMeans(n_clusters=numberOfClusters, random_state=0).fit_predict(text)
dataFrame['cluster'] = clusters
clusteredFrames = [dataFrame[dataFrame['cluster'] == id] for id in range(numberOfClusters)]   
featureNames = vector.get_feature_names()
text = panda.DataFrame(text.todense())
text = text.groupby(clusters)
text = text.mean()

#Calculates the key words from each cluster and prints them
for i, x in text.iterrows():
    keywords = [featureNames[j] for j in np.argsort(x)]
    cluster = clusteredFrames[i]
    print("Key words for Cluster " + str(i+1) + " (" + str(cluster.shape[0]) + " tweets): " +  ", ".join(keywords[-10:][::-1]))

#Initialise empty array
array=[]

#Appends the Clusters into a list of lists in order to get the largest cluster
for dataFrame in clusteredFrames:
    array.append(dataFrame.shape[0])

#Calculates the smallest, largest and average size of the clusters
mininum = min(array)
maximum = max(array)
average = sum(array)/len(array)

#Prints the data calculated above
print("Minimum number in a cluster: " + str(mininum)) 
print("Maximum number in a cluster: " + str(maximum))
print("Average number in a cluster: " + str(average))



