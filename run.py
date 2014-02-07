#!/root/screenshots/env/bin/python
import subprocess
import time


class PyshotX(object):
    webserver = None
    directory = 'screens/'
    levels = False
    childs = 1
    childrens = {}
    childrenStarted = {}

    def setChildrenProcesses(self, number):
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
            if children.poll() == 0:
                print 'process not running...restart'
                self.startChildren(processNumber)
            else:
                started = time.time() - self.childrenStarted[processNumber]
                if started > 60 * 10:
                    print 'kill and run new process'
                    children.kill()
                    self.startChildren(processNumber)

    def run(self):
        self.startWebServer()
        self.runChildrenProcesses()
        while True:
            self.checkProcesses()
            time.sleep(5)


if __name__ == '__main__':
    pyshotx = PyshotX()
    pyshotx.setUseLevels(True)
    pyshotx.setDirectory('/DATA1/screenshots/')
    pyshotx.setChildrenProcesses(10)

    pyshotx.run()
