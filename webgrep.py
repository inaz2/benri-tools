#!/usr/bin/env python

"""grep web page(s) by xpath

This script requires libxml2 and python-libxml2.

collect all links (with resolving relative path)
$ python webgrep.py '//a/@href' http://www.example.com/

collect all jpeg image links recursively
$ python webgrep.py -r '//a[contains(@href,".jpg")]/@href' http://www.example.com/
"""

import sys
import urllib2
import libxml2
from urlparse import urljoin, urldefrag

def webgrep(xpath, urls, is_recursive):
    root_url = urls[0]
    is_multiple_source = is_recursive or len(urls) > 1

    queue = [(url, None) for url in urls]
    visited = dict((url, True) for url in urls)

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
                if is_multiple_source:
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
    from optparse import OptionParser
    usage = "Usage: %prog [options] XPATH URL..."
    parser = OptionParser(usage=usage)
    parser.add_option('-r', '--recursive', action='store_true', dest='is_recursive', default=False, help='turn on recursive retrieving')
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.print_help()
        sys.exit(1)
    webgrep(args[0], args[1:], options.is_recursive)
