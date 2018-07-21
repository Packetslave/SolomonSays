#!/usr/bin/env python

import sys

import twitter
import xmltodict

doc = None
with open('proverbs.xml') as fd:
    doc = xmltodict.parse(fd.read())

root = doc['bible']['b']['c']

chapters = {}

for chapter in root:
    # Keep track of number of verses per chapter    
    chapters[chapter["@n"]] = len(chapter["v"])

BLACKLIST = frozenset([
    "1:1",  # intro to the book
    "1:2",  # intro to the book
    "1:3",  # intro to the book
    "1:4",  # intro to the book
    "1:5",  # intro to the book
])

#sys.path.append(".")
#import twitter_config as config
#new_status = "testing testing"
#twitter = Twitter(auth = OAuth(config.access_key,
#                               config.access_secret,
#                               config.consumer_key,
#                               config.consumer_secret))
#
#results = twitter.statuses.update(status = new_status)
#print("updated status: %s" % new_status)