#!/usr/bin/env python

import sys
import urllib2
import urllib
import json
from datetime import datetime, timedelta
import time

def twsearch(keyword):
    query = "?result_type=recent&rpp=100&lang=ja&include_entities=1&q=%s" % urllib.quote(keyword)

    while True:
        f = urllib2.urlopen("http://search.twitter.com/search.json" + query)
        data = json.loads(f.read())
        f.close()

        for result in reversed(data['results']):
            created_at = datetime.strptime(result['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
            created_at = created_at + timedelta(hours=9)    # tzinfo sucks (UTC -> JST)
            tweet_url = "http://twitter.com/%(from_user)s/status/%(id)s" % result
            text = result['text']
            for entity in result["entities"].get("media", {}):
                text = text.replace(entity["url"], "\x1b[36m%s\x1b[0m" % entity["expanded_url"], 1)
            for entity in result["entities"].get("urls", {}):
                text = text.replace(entity["url"], "\x1b[36m%s\x1b[0m" % entity["expanded_url"], 1)
            for entity in result["entities"].get("user_mentions", {}):
                text = text.replace("@%s" % entity["screen_name"], "\x1b[35m@%s\x1b[0m" % entity["screen_name"], 1)
            for entity in result["entities"].get("hashtags", {}):
                text = text.replace("#%s" % entity["text"], "\x1b[32m#%s\x1b[0m" % entity["text"], 1)
            line = u"\x1b[1;30m[%s]\x1b[0m \x1b[33m@%s\x1b[0m: %s \x1b[1;30m<%s>\x1b[0m" % (created_at.strftime('%Y-%m-%d %H:%M:%S'), result['from_user'], text.replace('\n', ' '), tweet_url)
            print line.encode('utf-8')

        query = data['refresh_url']
        time.sleep(60)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: python %s KEYWORD" % sys.argv[0]
        sys.exit(1)
    try:
        twsearch(sys.argv[1])
    except KeyboardInterrupt:
        pass
