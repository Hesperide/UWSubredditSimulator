import random
import praw
import datetime
import time
import configparser
import markovify
from html.parser import HTMLParser

markovify_tries = 1000
markovify_max_overlap_total=10
markovify_max_overlap_ratio=0.5
title_char_limit = 300
selftext_char_limit = 250

class Markovifier(markovify.Text):

    html_parser = HTMLParser()

    def sentence_split(self, text):
        lines = text.splitlines()
        for i in range(len(lines)):
            lines[i] = self.html_parser.unescape(lines[i].strip())
            if not lines[i].endswith(('!', '?', '.')):
                lines[i] += '.'
        return markovify.split_into_sentences(" ".join(lines))

class Simulator:

    urls = []

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.config = dict(self.config['main'])

        self.session = praw.Reddit( 
                client_id = self.config['client_id'], 
                client_secret = self.config['client_secret'], 
                password = self.config['password'],
                user_agent = self.config['user_agent'], 
                username = self.config['username']
                )

    def get_from_time(self):
        return time.mktime(datetime.datetime.utcnow().timetuple()) - 60*60*24*50

    def get_submissions(self, from_time = None):
        if not from_time:
            from_time = self.get_from_time()
        return self.session.subreddit(self.config['subreddit']).submissions(start = from_time)

    def train_on_submissions(self, submissions = None):
        if not submissions:
            submissions = list(self.get_submissions())

        titles = []
        selftexts = []
        self.urls = []

        for s in submissions:
            titles.append(s.title)
            if not s.selftext:
                self.urls.append(s.url)
            else:
                selftexts.append(s.selftext)

        self.link_chance = len(self.urls) / len(submissions)
        self.title_model = Markovifier('\n'.join(titles), state_size = 2)
        self.selftext_model = Markovifier('\n'.join(selftexts), state_size = 3)
        self.average_selftext_length = sum([len(s) for s in selftexts]) / (len(selftexts) + 1)

    def generate_selftext_sentence(self):
        return self.selftext_model.make_sentence(
                tries = markovify_tries,
                max_overlap_total = markovify_max_overlap_total,
                max_overlap_ratio = markovify_max_overlap_ratio
                )

    def generate_title(self):
        return self.title_model.make_short_sentence(
                tries = markovify_tries,
                max_overlap_total = markovify_max_overlap_total,
                max_overlap_ratio = markovify_max_overlap_ratio,
                char_limit = title_char_limit
                )

    def post_submission(self):
        title = self.generate_title()
        if random.random() < self.link_chance:
            self.session.subreddit(self.config['target_subreddit']).submit(title, selftext = None, url = random.choice(self.urls))
        else:
            selftext = ""
            while True:
                selftext += self.generate_selftext_sentence() + ' '
                if len(selftext) >= min(selftext_char_limit, self.average_selftext_length):
                    break
            self.session.subreddit(self.config['target_subreddit']).submit(title, selftext = selftext, url = None)

'''
submission = reddit.submission(id=n[0])
print('Text :' + submission.selftext)
print('Score :' + str(submission.score))
print('Visited :' + str(submission.visited))
for top_level_comment in submission.comments:
        print('Top Comments: ' + top_level_comment.body)
'''

sim = Simulator()
sim.train_on_submissions()
for i in range(5):
    sim.post_submission()
