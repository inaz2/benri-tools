#!/usr/bin/env python

import sys
import base64
import urllib2
import urllib
import json
from datetime import datetime, timedelta
import getpass
import re

def contains_japanese_character(s):
    # CJK_SYMBOLS_AND_PUNCTUATION | HIRAGANA | KATAKANA | CJK_UNIFIED_IDEOGRAPHS | HALFWIDTH_AND_FULLWIDTH_FORMS
    m = re.search(u'[\u3000-\u303F\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uFF00-\uFFEF]', s)
    return bool(m)

def format_tweet(result):
    created_at = datetime.strptime(result['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
    created_at = created_at + timedelta(hours=9)    # tzinfo sucks (UTC -> JST)
    tweet_url = "http://twitter.com/%s/status/%s" % (result['user']['screen_name'], result['id'])
    text = result['text']
    for entity in result["entities"].get("media", {}):
        text = text.replace(entity["url"], "\x1b[36m%s\x1b[0m" % entity["expanded_url"], 1)
    for entity in result["entities"].get("urls", {}):
        text = text.replace(entity["url"], "\x1b[36m%s\x1b[0m" % entity["expanded_url"], 1)
    for entity in result["entities"].get("user_mentions", {}):
        text = text.replace("@%s" % entity["screen_name"], "\x1b[35m@%s\x1b[0m" % entity["screen_name"], 1)
    for entity in result["entities"].get("hashtags", {}):
        text = text.replace("#%s" % entity["text"], "\x1b[32m#%s\x1b[0m" % entity["text"], 1)
    line = u"\x1b[1;30m[%s]\x1b[0m \x1b[33m@%s\x1b[0m: %s \x1b[1;30m<%s>\x1b[0m" % (created_at.strftime('%Y-%m-%d %H:%M:%S'), result['user']['screen_name'], text.replace('\n', ' '), tweet_url)
    return line

def twstream(keyword, username, password):
    if keyword:
        url = 'https://stream.twitter.com/1.1/statuses/filter.json'
        postdata = urllib.urlencode({'track': keyword})
    else:
        url = 'https://stream.twitter.com/1.1/statuses/sample.json'
        postdata = None

    req = urllib2.Request(url)
    authstr = base64.encodestring('%s:%s' % (username, password)).strip()
    req.add_header('Authorization', 'Basic %s' % authstr)
    if postdata:
        res = urllib2.urlopen(req, postdata)
    else:
        res = urllib2.urlopen(req)

    for line in res:
        result = json.loads(line)
        if not 'text' in result:
            continue
        if not keyword and result['user']['lang'] != 'ja':
            continue
        # if not keyword and not contains_japanese_character(result['text']):
        #     continue
        line = format_tweet(result)
        print line.encode('utf-8')

if __name__ == '__main__':
    sys.stderr.write('username: ')
    username = raw_input()
    password = getpass.getpass('password: ')

    if len(sys.argv) < 2:
        twstream(None, username, password)
    else:
        twstream(sys.argv[1], username, password)
