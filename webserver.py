#!/usr/bin/env python
import gevent
from gevent import wsgi
from gevent import queue
from urlparse import urlparse, parse_qs
import time
import redis
import multiprocessing
import hashlib
import Image
import os
import sys
import json
import urllib2


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
                 sw, parentPid, useLevels):
    secretWord = sw
    while True:
        try:
            #check if parent process exists, if not kill children
            if not os.path.exists("/proc/%s" % parentPid):
                sys.exit()

            resizeRedis = redisConnection.spop(resizeQueueKey)
            if resizeRedis is None:
                time.sleep(1)
            else:
                domain, screenshotsForResizing = resizeRedis.split('@')
                thumbnailsList = dict()

                screenshotsJson = json.loads(screenshotsForResizing)

                for deviceName, screenshot in screenshotsJson.iteritems():
                    screenshotPath = screenshot
                    thumbnailsList[deviceName] = dict()
                    thumbnailsList[deviceName]['screenshot'] = None
                    thumbnailsList[deviceName]['thumbnail'] = None

                    #check if phantomjs has created screenshot for this device
                    if not screenshot:
                        continue

                    #check if screenshot really exists
                    try:
                        open(screenshotPath, 'r')
                    except Exception:
                        continue

                    split = screenshotPath.split('/')
                    filename = split[-1]
                    del split[-1]
                    savePath = '/'.join(split)
                    domainDevice = filename.replace('.png', '')
                    domain, device = domainDevice.split('_')

                    domainHash = hashlib.md5(domain + secretWord).hexdigest()

                    levels = '/%s/%s/%s/%s' % (domainHash[0],
                                               domainHash[1],
                                               domainHash[2],
                                               domainHash[3])

                    if useLevels:
                        savePath = savePath + '%s' % levels
                    thumbnailFilename = '%s/%s_%s_thumbnail.jpg' % (savePath,
                                                                    domainHash,
                                                                    device)
                    screenshot = ProcessScreenshot.open(screenshotPath)
                    if device == 'iPhone':
                        screenshot.saveThumbnail(1180,
                                                 210,
                                                 thumbnailFilename,
                                                 quality=60)
                    elif device == 'iPad':
                        screenshot.saveThumbnail(342,
                                                 256,
                                                 thumbnailFilename,
                                                 quality=60)
                    elif device == 'laptop':
                        screenshot.saveThumbnail(232,
                                                 139,
                                                 thumbnailFilename,
                                                 quality=60)

                    screenshotFilename = '%s/%s_%s.jpg' % (savePath,
                                                           domainHash,
                                                           device)
                    screenshot = ProcessScreenshot.open(screenshotPath)
                    screenshot.save(screenshotFilename, 60)

                    thumbnailsList[deviceName] = dict()
                    thumbnailsList[deviceName]['screenshot'] = screenshotFilename
                    thumbnailsList[deviceName]['thumbnail'] = thumbnailFilename

                    os.remove(screenshotPath)

                redisKey = '%s_done' % domain
                redisConnection.set(redisKey, json.dumps(thumbnailsList))
                redisConnection.expire(redisKey, 60)
        except Exception, err:
            print 'EXCEPTION, ERROR'
            print err
            time.sleep(1)
            sys.stdout.flush()


def waitForScreenshot(domain, screenshotsQueue):
    started = int(time.time())
    while True:
        getScreenshots = redisConnection.get('%s_done' % domain)
        if getScreenshots is not None:
            redisConnection.delete('%s_done' % domain)
            screenshotsQueue.put(getScreenshots)
            screenshotsQueue.put(StopIteration)
            break
        else:
            gevent.sleep(1)
            if int(time.time()) - started >= 60:
                screenshotsQueue.put('error')
                screenshotsQueue.put(StopIteration)
                break


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
        query = parse_qs(urlparse('?' + queryString).query)
        screenshotsJson = query['screenshots'][0]
        domain = query['domain'][0]
        screenshotsJson = urllib2.unquote(screenshotsJson)
        redisConnection.sadd(resizeQueueKey, '%s@%s' % (domain,
                                                        screenshotsJson))
        return ['okay']

    if path == CREATE_SCREENSHOT:
        screenshots = queue.Queue()
        try:
            queryKey, domain = queryString.split('=')
        except Exception:
            return ['error']
        redisConnection.sadd(screenshotsQueueKey, domain)
        gevent.spawn(waitForScreenshot, domain, screenshots)
        print 'return screenshots to the client'
        return screenshots

    return ['error']


if __name__ == '__main__':
    useLevels = False
    if 'levels' in sys.argv:
        useLevels = True
    parentPid = os.getpid()
    GET_DOMAIN_URL = '/get_domain'
    RESIZE_URL = '/resize'
    CREATE_SCREENSHOT = '/create'

    screenshotsQueueKey = 'screenshots_queue'
    resizeQueueKey = 'resize_queue'
    secretWord = 'iamnacholibre'

    redisConnection = redis.StrictRedis(host='localhost', port=6379, db=0)

    resizeProcess = multiprocessing.Process(target=resizeDaemon,
                                            args=(redisConnection,
                                                  screenshotsQueueKey,
                                                  resizeQueueKey,
                                                  secretWord,
                                                  parentPid,
                                                  useLevels))
    resizeProcess.start()

    wsgi.WSGIServer(('', 8088), server).serve_forever()
