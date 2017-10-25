# -*- coding: utf-8 -*-

import os
import re
import requests
import time
import boto3
import urllib
import urlparse
import time
import datetime
from os.path import join, dirname
from bs4 import BeautifulSoup
from boto3.session import Session
from dotenv import load_dotenv
from multiprocessing import Pool, Process

baseUrl = "http://mabinogi.nexon.co.jp"
tradeUrl = "/community/tradeBoardList.asp?sv="
taServer = "ta"
maServer = "ma"
ruServer = "ru"
tableName = "mabinogi_trade_entries"
ttlDays = 5

load_dotenv(join(dirname(__file__), ".env"))
session = Session(
    aws_access_key_id=os.environ["MOONYA_ACCESS_ID"],
    aws_secret_access_key=os.environ["MOONYA_ACCESS_SECRET"],
    region_name=os.environ["MOONYA_REGION_NAME"])
dynamodb = session.resource("dynamodb")
table = dynamodb.Table(tableName)

def lambda_handler(event, context):
    processes = []
    p = Process(target=scrapeTarlach)
    p.start()
    processes.append(p)
    p = Process(target=scrapeMari)
    p.start()
    processes.append(p)
    p = Process(target=scrapeRuairi)
    p.start()
    processes.append(p)

    for p in processes:
        p.join()

def scrapeTarlach():
    url = baseUrl + tradeUrl + taServer
    scrape(url)

def scrapeMari():
    url = baseUrl + tradeUrl + maServer
    scrape(url)

def scrapeRuairi():
    url = baseUrl + tradeUrl + ruServer
    scrape(url)

def scrape(url):
    body = getHtmlBody(url)
    urls = parseTradeListHtml(body)

    for url in urls:
        match = re.search(r"ix\=(\d*)\&", url)
        tradeId = match.group(1)
        item = table.get_item(Key={"trade_id": int(tradeId)})
        if "Item" in item:
            continue
        time.sleep(3)
        body = getHtmlBody(url)
        doc = parseTradeEntryHtml(body)
        saveDoc(table, doc)

def getHtmlBody(url):
    res = requests.get(url)
    if res.status_code != 200:
        print("Request Error: " + str(res.status_code))
    return res.text

def parseTradeListHtml(body):
    soup = BeautifulSoup(body, "html.parser")
    entryUrls = []
    for a in soup.select("[class^='list-title'] > p > a"):
        if a.get("href") != None:
            entryUrls.append(baseUrl + a.get("href"))
    return entryUrls

def parseTradeEntryHtml(body):
    soup = BeautifulSoup(body, "html.parser")
    title = parseTitle(soup)
    user = parseUserName(soup)
    server = parseServerName(soup)
    tradeType = parseTradeType(soup)
    date = parseDate(soup)
    bodyText = parseBodyText(soup)
    url = parseUrl(soup)
    tradeId = parseTradeId(soup)
    timestamp = genTTLEpoch()
    return {
        "trade_id": tradeId,
        "title": title,
        "user": user,
        "server": server,
        "type": tradeType,
        "date": date,
        "text": bodyText,
        "url": url,
        "timestamp": timestamp,
    }

def saveDoc(table, doc):
    item = table.get_item(Key={"trade_id": int(doc["trade_id"])})
    if "Item" in item:
        print("Already saved. Trade Id: " + str(doc["trade_id"]))
        return
    table.put_item(Item=doc)
    print("Saved entry. Trade Id: " + str(doc["trade_id"]))

def parseTitle(soup):
    soup.find(class_="detail-title-txt").string.strip()
    title = soup.find(class_="detail-title-txt")
    if title != None:
        return title.string.strip()
    else:
        return ""

def parseUserName(soup):
    user = soup.find(id="contributor-name")
    if user != None:
        return user.string.strip()
    else:
        return ""

def parseServerName(soup):
    imgs = soup.select("[id='contributor-server'] > img")
    if imgs == None:
        return ""
    for img in imgs:
        if re.match(r".*tarlach.*", img.get("src")):
            return taServer
        if re.match(r".*mari.*", img.get("src")):
            return maServer
        if re.match(r".*ruairi.*", img.get("src")):
            return ruServer
        return ""

def parseTradeType(soup):
    imgs = soup.select("[class='detail-title-icn'] > img")
    if imgs == None:
        return ""
    for img in imgs:
        if re.match(r".*buy.*", img.get("src")):
            return "買取"
        if re.match(r".*sell.*", img.get("src")):
            return "販売"
        if re.match(r".*barter.*", img.get("src")):
            return "交換"
        if re.match(r".*other.*", img.get("src")):
            return "その他"

def parseDate(soup):
    date = soup.find(id="contributor-date")
    if date != None:
        return date.string.strip()
    else:
        return ""

def parseBodyText(soup):
    bodies = soup.select("[id='detail-main'] > p")
    if bodies == None:
        return ""
    text = ""
    for body in bodies:
        for content in body.contents:
            if content == None:
                continue
            if content.name == "br":
                text += "\n"
                continue
            if content.string == None:
                continue
            text += content.string.strip()
    return text

def parseUrl(soup):
    url = soup.find(id="commentRtnUrl")
    if url == None:
        return ""
    return url.get("value")

def parseTradeId(soup):
    url = soup.find(id="commentRtnUrl")
    if url == None:
        return ""
    result = urlparse.urlparse(url.get("value"))
    params = urlparse.parse_qs(result.query)
    return int(params["ix"][0])

def genTTLEpoch():
    now = datetime.datetime.now()
    ttl = now + datetime.timedelta(days=ttlDays)
    epoch = int(time.mktime(ttl.timetuple()))
    return epoch


if __name__ == "__main__":
    lambda_handler(None, None)