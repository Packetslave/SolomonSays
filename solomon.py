#!/usr/bin/env python

import calendar
import random
import os
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

now = int(calendar.timegm(time.gmtime()))

# Read the blacklist of verses we've posted recently

response = table.scan(
    FilterExpression=Attr('last_updated').gt(now - BLACKLIST_SECS)
)
for i in response['Items']:
    print "Adding %s to blacklist (posted %.1f days ago)" % (
        i["verse"],
        (now - i["last_updated"]) / (60 * 60 * 24))
    BLACKLIST.add(i['verse'])

# Read the XML verses file

doc = None
with open('proverbs.xml') as fd:
    doc = xmltodict.parse(fd.read())

root = doc['bible']['b']['c']

# Keep track of number of verses per chapter and the total number

chapters = {}
verses = 0

for chapter in root:
    chapters[chapter["@n"]] = len(chapter["v"])
    verses += len(chapter["v"])

# Pick a verse to post, skip duplicates and blacklisted verses

while True:
    chapter_idx = random.randint(1, len(chapters))
    verse_idx = random.randint(1, len(root[chapter_idx-1]['v']))
    verse_key = "%s:%s" % (chapter_idx, verse_idx)
    if verse_key not in BLACKLIST:
        break

verse = root[chapter_idx - 1]['v'][verse_idx - 1]['#text']

# Post to twitter

new_status = "%s (Proverbs %s:%s NIV)" % (verse, chapter_idx, verse_idx)
print("status: %s" % new_status)

if 'DEBUG' in os.environ:
    sys.exit(0)

twitter = twitter.Twitter(auth=twitter.OAuth(config.access_key,
                                             config.access_secret,
                                             config.consumer_key,
                                             config.consumer_secret))
results = twitter.statuses.update(status=new_status)

# Update DynamoDB with tinmestamp for the verse we just posted

table.update_item(
  Key={
    "verse": "%s:%s" % (chapter_idx, verse_idx),
  },
  UpdateExpression='SET last_updated = :val1',
  ExpressionAttributeValues={
      ':val1': now,
  }
)
