#!/usr/bin/env python
from gevent import wsgi
import time
import redis
import multiprocessing
import hashlib
import Image
import os
import sys


class Screenshot(object):
    def __init__(self, image):
        self.image = image

    def saveThumbnail(self, thumbWidth, thumbHeight, filename, quality=100):
        self.image.thumbnail((thumbWidth, thumbHeight), Image.ANTIALIAS)
        self.image.save(filename, 'JPEG', quality=80)

    def save(self, filename, quality=100):
        self.image.save(filename, 'JPEG', quality=quality)


class ProcessScreenshot(object):
    @staticmethod
    def open(screenshotPath):
        screenshot = Image.open(screenshotPath)
        return Screenshot(screenshot)


def resizeDaemon(redisConnection, screenshotsQueueKey, resizeQueueKey,
                 sw, parentPid):
    secretWord = sw
    while True:
        if not os.path.exists("/proc/%s" % parentPid):
            sys.exit()
        screenshotPath = redisConnection.spop(resizeQueueKey)
        if screenshotPath is None:
            time.sleep(1)
        else:
            split = screenshotPath.split('/')
            filename = split[-1]
            del split[-1]
            screensPath = '/'.join(split)
            domain = filename.replace('.png', '')
            domainHash = hashlib.md5(domain + secretWord).hexdigest()

            thumbnailFilename = '%s/%s_thumbnail.jpg' % (screensPath,
                                                         domainHash)
            screenshot = ProcessScreenshot.open(screenshotPath)
            screenshot.saveThumbnail(227, 128, thumbnailFilename, quality=60)

            screenshotFilename = '%s/%s.jpg' % (screensPath, domainHash)
            screenshot = ProcessScreenshot.open(screenshotPath)
            screenshot.save(screenshotFilename, 60)

            os.remove(screenshotPath)


def server(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    path = env['PATH_INFO']
    queryString = env['QUERY_STRING']

    if path == GET_DOMAIN_URL:
        domain = redisConnection.spop(screenshotsQueueKey)
        if domain:
            return [domain]
        else:
            return ['empty']

    if path == RESIZE_URL:
        try:
            queryKey, resizePath = queryString.split('=')
        except Exception:
            return ['error']
        print 'resize'
        redisConnection.sadd(resizeQueueKey, resizePath)
        return ['okay']

    return ['error']


if __name__ == '__main__':
    parentPid = os.getpid()
    GET_DOMAIN_URL = '/get_domain'
    RESIZE_URL = '/resize'

    screenshotsQueueKey = 'screenshots_queue'
    resizeQueueKey = 'resize_queue'
    secretWord = 'iamnacholibre'

    redisConnection = redis.StrictRedis(host='localhost', port=6379, db=0)

    resizeProcess = multiprocessing.Process(target=resizeDaemon,
                                            args=(redisConnection,
                                                  screenshotsQueueKey,
                                                  resizeQueueKey,
                                                  secretWord,
                                                  parentPid))
    resizeProcess.start()

    wsgi.WSGIServer(('', 8088), server).serve_forever()
