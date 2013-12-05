pyshotx
=======
##Required software
* gevent - pip install gevent
* phantomjs (1.9 or up) - http://phantomjs.org
* redis - http://redis.io
* redis-py - pip install redis
* Python Imaging Library (PIL) - pip install PIL

gevent is used for the web server.
phantomjs is used for creating the actual screenshots.
redis is used for synchronizing between the server and the image resizing
process.
redis-py is redis client for python
PIL is used for resizing the screenshots.

##Usage
    ./run.sh -e -d screens/
Open: http://0.0.0.0:8088/create?domain=ebay.com and wait for the screenshots.

If nothing happens check the logfiles:
* webserver.log
* sphantomjs_children_1.log
