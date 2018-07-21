#!/usr/bin/env python

import random
import sys

import twitter
import xmltodict

sys.path.append(".")
import twitter_config as config

BLACKLIST = frozenset([
    "1:1",  # intro to the book
    "1:2",  # intro to the book
    "1:3",  # intro to the book
    "1:4",  # intro to the book
    "1:5",  # intro to the book
])

doc = None
with open('proverbs.xml') as fd:
    doc = xmltodict.parse(fd.read())

root = doc['bible']['b']['c']

chapters = {}
verses = 0

for chapter in root:
    # Keep track of number of verses per chapter and the total number
    chapters[chapter["@n"]] = len(chapter["v"])
    verses += len(chapter["v"])

# TODO: keep track of posted verses and don't select one that's been posted
# in the past ${verses} days. That should eliminate duplicates.

chapter_idx = random.randint(1, len(chapters))
verse_idx = random.randint(1, len(root[chapter_idx-1]['v']))
verse = root[chapter_idx - 1]['v'][verse_idx - 1]['#text']

new_status = "%s (Proverbs %s:%s NIV)" % (verse, chapter_idx, verse_idx)

twitter = twitter.Twitter(auth=twitter.OAuth(config.access_key,
                                               config.access_secret,
                                               config.consumer_key,
                                               config.consumer_secret))

results = twitter.statuses.update(status=new_status)
print("updated status: %s" % new_status)
