# -*- coding: utf-8 -*-

import os
import twitter
from os.path import join, dirname
from dotenv import load_dotenv

MAX_TEXT_LENGTH = 50

def lambda_handler(event, context):
    print(event)
    load_dotenv(join(dirname(__file__), ".env"))

    records = event["Records"]
    for record in records:
        if record["eventName"] != "INSERT":
            continue
        print(record)
        item = record["dynamodb"]["NewImage"]
        url = item["url"]["S"]
        title = item["title"]["S"]
        text = compress_text(item["text"]["S"])
        tradeType = item["type"]["S"]
        server = item["server"]["S"]
        user = item["user"]["S"]

        message = "[%s] %s(%s)\n%s\n%s" % (tradeType, title, user, text, url)
        if server == "ta":
            tweet_tarlach(message)
        elif server == "ma":
            tweet_mari(message)
        elif server == "ru":
            tweet_ruairi(message)

def compress_text(text):
    return text if len(text) <= MAX_TEXT_LENGTH else "%s ..." % text[:MAX_TEXT_LENGTH]

def tweet_tarlach(message):
    print(message)
    auth = auth_twitter(
        os.environ["TARLACH_TWITTER_CONSUMER_KEY"],
        os.environ["TARLACH_TWITTER_CONSUMER_SECRET"],
        os.environ["TARLACH_TWITTER_TOKEN"],
        os.environ["TARLACH_TWITTER_TOKEN_SECRET"])
    t = twitter.Twitter(auth=auth)
    t.statuses.update(status=message)

def tweet_mari(message):
    print(message)
    auth = auth_twitter(
        os.environ["MARI_TWITTER_CONSUMER_KEY"],
        os.environ["MARI_TWITTER_CONSUMER_SECRET"],
        os.environ["MARI_TWITTER_TOKEN"],
        os.environ["MARI_TWITTER_TOKEN_SECRET"])
    t = twitter.Twitter(auth=auth)
    t.statuses.update(status=message)

def tweet_ruairi(message):
    print(message)
    #auth = auth_twitter(
    #    os.environ["RUAIRI_TWITTER_CONSUMER_KEY"],
    #    os.environ["RUAIRI_TWITTER_CONSUMER_SECRET"],
    #    os.environ["RUAIRI_TWITTER_TOKEN"],
    #    os.environ["RUAIRI_TWITTER_TOKEN_SECRET"])
    #t = twitter.Twitter(auth=auth)
    #t.statuses.update(status=message)

def auth_twitter(consumer_key, consumer_secret, token, token_secret):
    return twitter.OAuth(
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        token=token,
        token_secret=token_secret)

if __name__ == "__main__":
    lambda_handler(None, None)