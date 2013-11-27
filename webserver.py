#!/usr/bin/env python
from gevent import wsgi
import time
import redis
import multiprocessing
import hashlib
import Image
import os


def resizeDaemon(redisConnection, screenshotsQueueKey, resizeQueueKey, sw):
    secretWord = sw
    while True:
        screenshotPath = redisConnection.spop(resizeQueueKey)
        if screenshotPath is None:
            time.sleep(1)
        else:
            split = screenshotPath.split('/')
            filename = split[-1]
            domain = filename.replace('.png', '')
            domainHash = hashlib.md5(domain + secretWord).hexdigest()
            image = Image.open(screenshotPath)
            image.thumbnail((227, 128), Image.ANTIALIAS)
            image.save('%s_thumbnail' % domainHash, 'PNG')
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
    GET_DOMAIN_URL = '/getDomain'
    RESIZE_URL = '/resize'

    screenshotsQueueKey = 'screenshots_queue'
    resizeQueueKey = 'resize_queue'
    secretWord = 'iamnacholibre'

    redisConnection = redis.StrictRedis(host='localhost', port=6379, db=0)

    resizeProcess = multiprocessing.Process(target=resizeDaemon,
                                            args=(redisConnection,
                                                  screenshotsQueueKey,
                                                  resizeQueueKey,
                                                  secretWord))
    resizeProcess.start()

    wsgi.WSGIServer(('', 8088), server).serve_forever()
