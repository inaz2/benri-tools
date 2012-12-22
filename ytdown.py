#!/usr/bin/env python

"""This script requires wget."""

import sys
import urllib2
import urllib
import re
import subprocess

def ytdown(url):
    f = urllib2.urlopen(url)
    content = f.read()
    f.close()

    vid = re.search(r'v=([^&]+)', url).group(1)
    while True:
        m = re.search(r'[^,]*itag=38[^,]*', content)
        if m:
            size = 'Original'
            break
        m = re.search(r'[^,]*itag=37[^,]*', content)
        if m:
            size = '1920x1080'
            break
        m = re.search(r'[^,]*itag=22[^,]*', content)
        if m:
            size = '1280x720'
            break
        m = re.search(r'[^,]*itag=18[^,]*', content)
        if m:
            size = '640x360'
            break
        raise Exception('mp4 video not found')
    params = dict(pair.split('=') for pair in m.group(0).split('\\u0026'))
    download_url = "%s&signature=%s" % (urllib.unquote(params['url']), params['sig'])
    code = subprocess.call(['wget', '-O', "YouTube %s (%s).mp4" % (vid, size), download_url])
    sys.exit(code)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print >>sys.stderr, "Usage: python %s URL" % sys.argv[0]
        sys.exit(1)
    ytdown(sys.argv[1])
