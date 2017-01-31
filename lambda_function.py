#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

def lambda_handler(event, context):
    url = 'http://www.google.co.jp'
    response = requests.get(url)
    if response.status_code == requests.codes.ok:
        print 'OK'
    else:
        print 'NG'

if __name__ == "__main__":
    lambda_handler({}, {})
