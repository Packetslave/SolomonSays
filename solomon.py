#!/usr/bin/env python

import calendar
import datetime
import random
import sys
import time

import boto3
from boto3.dynamodb.conditions import Key, Attr

import twitter
import xmltodict

sys.path.append(".")
import twitter_config as config

BLACKLIST = set([
    "1:1",  # intro to the book
    "1:2",  # intro to the book
    "1:3",  # intro to the book
    "1:4",  # intro to the book
    "1:5",  # intro to the book
])

BLACKLIST_SECS = 60 * 60 * 24 * 60

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(config.dynamodb_table)

now = int(time.time())

# Read the blacklist of verses we've posted recently

response = table.scan(
    FilterExpression=Attr('last_updated').gt(now - BLACKLIST_SECS)
)
for i in response['Items']:
    print "Adding %s to blacklist (posted %s)" % (
        i["verse"],
        (datetime.datetime.fromtimestamp(i["last_updated"])))
    BLACKLIST.add(i['verse'])

# Read the XML verses file

doc = None
with open('proverbs.xml') as fd:
    doc = xmltodict.parse(fd.read())

root = doc['bible']['b']['c']

# Keep track of number of verses per chapter and the total number.
# Could hardcode this (it's not like Proverbs is going to change)
# but it's a small set of data, so easy enough to just compute it.

chapters = {}
verses = 0

for chapter in root:
    chapters[chapter["@n"]] = len(chapter["v"])
    verses += len(chapter["v"])

# Pick a verse to post, skip duplicates and blacklisted verses

for _ in xrange(0, verses):
    chapter_idx = random.randint(1, len(chapters))
    verse_idx = random.randint(1, len(root[chapter_idx-1]['v']))
    verse_key = "%s:%s" % (chapter_idx, verse_idx)
    if verse_key not in BLACKLIST:
        break
else:
    sys.stderr.write("did not find a non-duplicate verse?!\n")
    sys.exit(1)

verse = root[chapter_idx - 1]['v'][verse_idx - 1]['#text']

# Post to twitter

new_status = "%s (Proverbs %s NIV)" % (verse, verse_key)
print("status: %s" % new_status)

twitter = twitter.Twitter(auth=twitter.OAuth(config.access_key,
                                             config.access_secret,
                                             config.consumer_key,
                                             config.consumer_secret))
results = twitter.statuses.update(status=new_status)

# Update DynamoDB with tinmestamp for the verse we just posted

table.update_item(
  Key={
    "verse": verse_key,
  },
  UpdateExpression='SET last_updated = :val1',
  ExpressionAttributeValues={
      ':val1': now,
  }
)
