#!/usr/bin/env python

import os
import random
import time
import httplib
import urlparse
import urllib2
import sys

from optparse import OptionParser

import threading

from pprint import pprint

g_options = None

g_parser = OptionParser(usage="usage: %prog [options] url")

g_parser.add_option(
    "-f", "--file", 
    help="output filename", metavar="FILE")

g_parser.add_option(
    "-d", "--dest", 
    help="destination directory", metavar="DIR")

def proxyCallback(option, optStr, value, parser):
    value = value.split(':', 1)
    port = 80
    if len(value) > 1:
        port = int(value[1])
    setattr(parser.values, option.dest,(value[0], port,))

g_parser.add_option(
    "-p", "--proxy", type=str, action="callback",
    callback=proxyCallback,
    help="http proxy server", metavar="SERVER:PORT")

g_parser.add_option(
    "-z", "--buffer", default=8192,
    help="buffer size", metavar="BYTES")

g_parser.add_option(
    "-l", "--limit", default=50*1024, type=int, action="callback",
    callback=lambda o,s,v,p: setattr(p.values, o.dest, v*1024),
    help="kbs limit", metavar="KBS")

g_parser.add_option(
    "-b", "--burst", default=70*1024, type=int, action="callback",
    callback=lambda o,s,v,p: setattr(p.values, o.dest, v*1024),
    help="burst limit", metavar="KBS")

g_parser.add_option(
    "-t", "--tick", default=0.01,
    help="tick interval", metavar="SECONDS")

g_bucketTokens = 0
g_exit = False

def parseArgv(argv):
    (options, args) = g_parser.parse_args()
    directory = options.dest
    if not directory:
        directory = os.getcwd()
    if not os.path.isdir(directory):
        return None
    if not args:
        return None
    url = args[0]
    filename = options.file
    if not filename:
        s = urlparse.urlsplit(url)
        _, filename = os.path.split(s.path)
    global g_options
    g_options = options
    fpath = os.path.join(directory, filename)
    print (g_options)
    pprint((url, fpath))
    return url, fpath
     
def takeTokens(tokencount):
    global g_bucketTokens
    if g_bucketTokens >= tokencount:
        g_bucketTokens -= tokencount
        return True
    return False

def printKbs(filename):
    def _():
        start, end = None, None
        tot, num = 0, 0
        while True:
            if g_exit:
                print "KB/s monitor exiting..."
                break
            end = time.time()
            size = g_byteCount
            if start is not None:
                inst = ((size - old) / 1024.0) / (end - start)
                tot += inst
                num += 1
                print "I: %.02f kb/s, A: %.02f kb/s" % (inst, tot / num)
            start = time.time()
            old = size
            for x in xrange(int(2 / g_options.tick)):
                if g_exit: break 
                time.sleep(g_options.tick)
    return _

def feedBucketTokens():
    global g_bucketTokens
    tokens_per = int(g_options.limit * g_options.tick)
    print "Tokens per tick: %d" % (tokens_per,)
    while True:
        if g_exit:
            print "Token feeder exiting..."
            break
        if g_bucketTokens >= g_options.burst:
            time.sleep(g_options.tick)
            continue
        g_bucketTokens += tokens_per
        time.sleep(g_options.tick)

class BucketReader (object):
    def __init__(self, fp):
        self.fp = fp
    def read(self, bufsize):
        while True:
            if takeTokens(bufsize):
                break
            time.sleep(g_options.tick)
        return self.fp.read(bufsize)
        
def prepareFile(filename):
    fp = open(filename, 'ab+')
    fp.seek(0, 2)
    fsize = fp.tell()
    return fp, fsize

def startHttpReq(url, fsize):
    headers = { "Range" : ("bytes=%d-" % fsize), }
    pprint(headers)
    split = urlparse.urlsplit(url)
    if split.scheme != "http":
        raise ValueError("Only http is supported")
    response = None
    responseHeaders = None
    server, port = None, 80
    if g_options.proxy:
        server, port = g_options.proxy
        h = httplib.HTTPConnection(server, port)
        h.request("GET", url, headers=headers)
        response = h.getresponse()
        responseHeaders = response.getheaders()
    else:
        response = urllib2.urlopen(url)
        responseHeaders = response.info().headers
    pprint(responseHeaders)
    return response

g_byteCount = 0

def readLoop(fpIn, fpOut):
    global g_byteCount
    while True:
        d = fpIn.read(g_options.buffer)
        fpOut.write(d)
        fpOut.flush()
        g_byteCount += len(d)
        if len(d) < g_options.buffer:
            break

def main():
    global g_exit
    try:
        params = parseArgv(sys.argv)
        if params is None:
            g_parser.print_help()
            raise SystemExit(1)
        url, filename = params
        threading.Thread(target=feedBucketTokens).start()
        threading.Thread(target=printKbs(filename)).start()
        fpOut, fsize = prepareFile(filename) 
        fpInput = startHttpReq(url, fsize)
        readLoop(BucketReader(fpInput), fpOut)
    except KeyboardInterrupt:
        pass
    finally:
        g_exit = True

if __name__ == '__main__':
    main()

# vim: et:sts=4:ts=4:sw=4:
