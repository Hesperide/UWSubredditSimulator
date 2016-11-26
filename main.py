import praw
import datetime
import time
import configparser

utc_now = datetime.datetime.utcnow()
dt = time.mktime(utc_now.timetuple()) - 60*60*24*2

config = configparser.ConfigParser()
config.read('config.ini')
config = config['main']

reddit = praw.Reddit(
        client_id = config['client_id'], 
        client_secret = config['client_secret'], 
        password = config['password'],
        user_agent = config['user_agent'], 
        username = config['username']
        )

n = list(reddit.subreddit('uwaterloo').submissions(start=dt))

for i in n:
	submission = reddit.submission(id=n[i])
	print('Text :' + submission.selftext)
	print('Score :' + str(submission.score))
	print('Visited :' + str(submission.visited))
	for top_level_comment in submission.comments:
		print('Top Comments: ' + top_level_comment.body)
