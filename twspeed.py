#!/usr/bin/env python

import sys
import urllib2
import urllib
import json
from datetime import datetime, timedelta

def total_seconds(td):
    return float(td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6

def twspeed(keyword):
    query = "?result_type=recent&rpp=100&q=%s" % urllib.quote(keyword)

    f = urllib2.urlopen("http://search.twitter.com/search.json" + query)
    data = json.loads(f.read())
    f.close()

    results = data['results']
    last = datetime.strptime(results[0]['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
    first = datetime.strptime(results[-1]['created_at'], '%a, %d %b %Y %H:%M:%S +0000')
    return len(results) * 60 / total_seconds(last - first)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: python %s KEYWORD..." % sys.argv[0]
        sys.exit(1)
    for keyword in sys.argv[1:]:
        print "%s: %.2f tweets/min" % (keyword, twspeed(keyword))
