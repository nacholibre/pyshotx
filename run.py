#!/usr/bin/env python
import subprocess
import time
import os


class PyshotX(object):
    webserver = None
    directory = 'screens/'
    levels = False
    childs = 1
    childrens = {}
    childrenStarted = {}

    def childrenProcesses(self, number):
        self.childs = number

    def setDirectory(self, directory):
        self.directory = directory

    def getDirectory(self):
        return self.directory

    def getChildrenProcesses(self):
        return self.childs

    def setUseLevels(self, use=False):
        self.levels = use

    def getUseLevels(self):
        return self.levels

    def startWebServer(self):
        args = ['./webserver.py']
        if self.getUseLevels():
            args.append('levels')
        webserverLog = open('webserver.log', 'w')
        webserver = subprocess.Popen(['./webserver.py'], stdout=webserverLog)
        self.webserver = webserver

    def startChildren(self, processNumber):
        processLog = open('children_%s.log' % processNumber, 'w')
        process = subprocess.Popen(['phantomjs',
                                   'screenshot.js',
                                   self.getDirectory()],
                                   stdout=processLog)

        self.childrenStarted[processNumber] = time.time()
        self.childrens[processNumber] = process

    def runChildrenProcesses(self):
        for processNumber in xrange(0, self.getChildrenProcesses()):
            self.startChildren(processNumber)

    def checkProcesses(self):
        for processNumber, children in self.childrens.iteritems():
            running = os.path.exists('/proc/%s' % children.pid)
            if not running:
                self.startChildren(processNumber)
            else:
                if self.childrenStarted[processNumber] > 60*10:
                    children.kill()
                    self.startChildren(processNumber)

    def run(self):
        self.startWebServer()
        self.runChildrenProcesses()
        while True:
            time.sleep(5)


if __name__ == '__main__':
    pyshotx = PyshotX()

    pyshotx.run()
