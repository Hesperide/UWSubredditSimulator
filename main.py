import praw
import datetime
import time

utc_now = datetime.datetime.utcnow()
dt = time.mktime(utc_now.timetuple()) - 60*60*24*2

def login():
    r = praw.Reddit(app_ua)
    r.set_oauth_app_info(app_id, app_secret, app_uri)
    r.refresh_access_information(app_refresh)
    return r

reddit = praw.Reddit(client_id=app_id, client_secret=app_secret,
                     password='chopsticks2016', user_agent=app_ua,
                     username='Rubikwindow')

n = list(reddit.subreddit('uwaterloo').submissions(start=dt)) ##this is a generator

for i in n:
	submission = reddit.submission(id=n[i])
	print('Text :' + submission.selftext)
	print('Score :' + str(submission.score))
	print('Visited :' + str(submission.visited))
	for top_level_comment in submission.comments:
		print('Top Comments: ' + top_level_comment.body)
