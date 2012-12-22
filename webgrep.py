#!/usr/bin/env python

"""grep web page(s) by xpath

This script requires libxml2 and python-libxml2.

collect all links (with resolving relative path)
$ python webgrep.py '//a/@href' http://www.example.com/

collect all jpeg image links recursively
$ python webgrep.py '//a[contains(@href,".jpg")]/@href' http://www.example.com/*
"""

import sys
import urllib2
import libxml2
from urlparse import urljoin, urldefrag

def webgrep(xpath, root_url, is_recursive):
    queue = [(root_url, None)]
    visited = {}
    visited[root_url] = True

    while len(queue) > 0:
        (url, referrer) = queue.pop(0)

        req = urllib2.Request(url)
        if referrer:
            req.add_header('Referer', referrer)
        try:
            f = urllib2.urlopen(req)
            content_type = f.info().gettype()
            if not content_type in ('text/html', 'application/xhtml+xml'):
                f.close()
                continue
            content = f.read()
            f.close()
        except urllib2.URLError as e:
            print >>sys.stderr, "%s: %s" % (url, e)
            continue

        try:
            doc = libxml2.htmlReadMemory(content, len(content), url, None, libxml2.HTML_PARSE_RECOVER | libxml2.HTML_PARSE_NOERROR | libxml2.HTML_PARSE_NOWARNING | libxml2.HTML_PARSE_NONET)
            ctx = doc.xpathNewContext()
            for node in ctx.xpathEvalExpression(xpath):
                content = node.content.strip()
                if node.type == 'attribute' and node.name in ('href', 'src'):
                    content = urljoin(url, content)
                if is_recursive:
                    print "%s:%s" % (url, content)
                else:
                    print content
            if is_recursive:
                for node in ctx.xpathEvalExpression('//a/@href'):
                    (next_url, fragment) = urldefrag(urljoin(url, node.content))
                    if next_url.startswith(root_url) and not next_url in visited:
                        queue.append((next_url, url))
                        visited[next_url] = True
            ctx.xpathFreeContext()
            doc.freeDoc()
        except libxml2.treeError as e:
            print >>sys.stderr, "%s: %s" % (url, e)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print >>sys.stderr, "Usage: python %s XPATH URL[*]" % sys.argv[0]
        sys.exit(1)
    if sys.argv[2][-1] == '*':
        webgrep(sys.argv[1], sys.argv[2][:-1], True)
    else:
        webgrep(sys.argv[1], sys.argv[2], False)
