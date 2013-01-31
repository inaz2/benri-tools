#!/usr/bin/env python

import sys
import urllib2
import urllib
import re
import subprocess
from HTMLParser import HTMLParser

def html_unescape(s):
    return HTMLParser.unescape.__func__(HTMLParser, s)

def xvdown(url):
    f = urllib2.urlopen(url)
    content = f.read()
    f.close()

    vid = url.split('/')[3]
    m = re.search(r' <h2>(.+) <span class="duration">', content)
    if m:
        title = html_unescape(m.group(1))
    else:
        raise Exception('invalid page title')
    m = re.search(r'flashvars="([^"]+)"', content)
    if m:
        flashvars = html_unescape(m.group(1))
    else:
        raise Exception('flv video not found')
    d = dict(pair.split('=') for pair in flashvars.split('&'))
    flv_url = urllib.unquote(d['flv_url'])
    code = subprocess.call(['wget', '-O', "[XVIDEOS][%s] %s (%sx%s).flv" % (vid, title, d['width'], d['height']), flv_url])
    sys.exit(code)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: %s URL..." % sys.argv[0]
        sys.exit(1)
    for url in sys.argv[1:]:
        xvdown(url)
