#!/usr/bin/env python
import subprocess
import time


class PyshotX(object):
    webserver = None
    directory = 'screens/'
    levels = False
    childs = 1

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

    def runChildrenProcesses(self):
        childrens = []
        for processNumber in xrange(0, self.getChildrenProcesses()):
            processLog = open('children_%s.log' % processNumber, 'w')
            process = subprocess.Popen(['phantomjs',
                                       'screenshot.js',
                                       self.getDirectory()],
                                       stdout=processLog)
            childrens.append(process)

    def run(self):
        self.startWebServer()
        self.runChildrenProcesses()
        while True:
            time.sleep(5)


if __name__ == '__main__':
    pyshotx = PyshotX()

    pyshotx.run()
