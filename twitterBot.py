import download, autotune, threading, random, tweepy, time, os
from subprocessHelper import *

#I use a weird tweepy mod that fixes video upload to make this work

APIkey = r"TOKEN"
APIsecretKey = r"TOKEN"
AccessToken = r"TOKEN-TOKEN"
AccessTokenSecret = r"TOKEN"
auth = tweepy.OAuthHandler(APIkey, APIsecretKey)
auth.set_access_token(AccessToken, AccessTokenSecret)
api = tweepy.API(auth)

directory = "files"

def getID(obj):
	return obj._json['id']

def getIDlist(ls):
	return [getID(i) for i in ls]

def threadedProcess(tweetID, url, song, tagName):
	try:
		filename = directory + '/' + str(random.random()) + '.mp4'
		download.download(filename, url, duration = 2 * 60)
		if type(result := autotune.autotuneURL(filename, song)) == str:
			upload_result = api.media_upload(filename, media_category = 'tweet_video')
			api.update_status(media_ids = [upload_result.media_id], status = '@' + tagName, in_reply_to_status_id = tweetID)
			print("SUCCESS", tweetID, song, tagName)
			os.remove(filename)
		else:
			print("ERROR", tweetID, song, tagName, result)
	except Exception as e:
		print("ERROR", e)

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


while 1:
	try:
		mostRecentID = getID(list(api.mentions_timeline(count = 1, tweet_mode = 'extended'))[0])
		break
	except Exception as e:
		print(e)
		time.sleep(45)
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
		if tweet._json['user']['screen_name'] == "autotunebot":
			continue
		result = testTweet(tweet)
		if result[1]:
			threadedProcess(*result, tweet._json['user']['screen_name'])
		else:
			if (topID := tweet._json['in_reply_to_status_id_str']) is not None:
				topTweet = api.get_status(topID, tweet_mode = 'extended')
				topResult = testTweet(topTweet)
				threadedProcess(result[0], topResult[1], result[2], tweet._json['user']['screen_name'])
		
	time.sleep(20)
