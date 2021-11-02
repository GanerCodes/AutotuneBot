import download, autotune, threading, random, tweepy, time, os, json
from subprocessHelper import *
from os import remove, path, makedirs

tokens = json.load(open("tokens.json"))
APIkey = tokens["twitterAPIkey"]
APIsecretKey = tokens["twitterAPIsecretKey"]
AccessToken = tokens["twitterAccessToken"]
AccessTokenSecret = tokens["twitterAccessTokenSecret"]
auth = tweepy.OAuthHandler(APIkey, APIsecretKey)
auth.set_access_token(AccessToken, AccessTokenSecret)
api = tweepy.API(auth)

directory = "files"

def getID(obj):
	return obj._json['id']

def getIDlist(ls):
	return [getID(i) for i in ls]

def threadedProcess(tweetID, url, song, tagName):
	filename = directory + '/' + str(random.random()) + '.mp4'
	download.download(filename, url, duration = 2 * 60)
	if type(autotune.autotuneURL(filename, song)) == str:
		upload_result = api.media_upload(filename)
		api.update_status(media_ids = [upload_result.media_id], status = '@' + tagName, in_reply_to_status_id = tweetID)
		print("SUCCESS", tweetID, song, tagName)
		os.remove(filename)
	else:
		print("ERROR", tweetID, song, tagName)

def testTweet(tweet):
	tweetText = ' '.join(filter(lambda x: x.strip()[0] != '@', tweet.full_text.split()))
	if 'media' in tweet.entities:
		for i in tweet.entities['media']:
			tweetText = tweetText.replace(i['url'], '')
		if "media" in tweet.entities:
			mediaList = list(filter(lambda x: x.split('/')[-2] == 'video', map(lambda x: x['expanded_url'], tweet.entities["media"])))
			if len(mediaList) > 0:
				return [tweet.id, mediaList[0], tweetText]
	return [tweet.id, None, tweetText]


mostRecentID = getID(list(api.mentions_timeline(count = 1, tweet_mode = 'extended'))[0]) - 1
print("Most recent tweet ID:", mostRecentID)

mentionsList, ignoreList = [], []
while 1:
	mentionsList = list(api.mentions_timeline(since_id = mostRecentID, count = 10, tweet_mode = 'extended'))
	if len(mentionsList) == 0:
		time.sleep(20)
		continue
	mostRecentID = getID(mentionsList[0])
	activeList = [i for i in mentionsList if getID(i) not in ignoreList]
	ignoreList += getIDlist(activeList)
	for tweet in activeList:
		# print(tweet)
		result = testTweet(tweet)
		if result[1]:
			threadedProcess(*result, tweet._json['user']['screen_name'])
		else:
			if (topID := tweet._json['in_reply_to_status_id_str']) is not None:
				try:
					topTweet = api.get_status(topID, tweet_mode = 'extended')
					topResult = testTweet(topTweet)
					threadedProcess(result[0], topResult[1], result[2], tweet._json['user']['screen_name'])
				except Exception as e:
					print(f"Error procesing tweet: {e}")
		
	time.sleep(20)