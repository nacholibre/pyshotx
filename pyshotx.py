#!/usr/bin/env python
from selenium import webdriver


class Browser(object):
    _webdriverPointer = None
    _webdriver = None
    device = None
    options = webdriver.ChromeOptions()

    def __init__(self, webdriverPointer):
        self._webdriverPointer = webdriverPointer

    def get(self, url):
        self.webdriver = self._webdriverPointer(chrome_options=self.options)
        try:
            self.webdriver.get(url)
        except Exception, err:
            print 'Get Exception', err
            self.quit()

    def setDevice(self, device):
        self.device = device
        self.addOptions(self.device)

    def setScreenResolution(self):
        screenResolution = self.device.getScreenResolution()
        if screenResolution:
            screenWidth, screenHeight = self.device.getScreenResolution()
            webdriver.set_window_size(screenWidth, screenHeight)

    def saveScreenshot(self, filename):
        self.webdriver.save_screenshot(filename)

    def quit(self):
        self.webdriver.quit()

    def addOptions(self, device):
        userAgent = device.getUseragent()
        if userAgent:
            self.options.add_argument('--user-agent=%s' %
                                      device.getUseragent())


class Device(object):
    userAgent = None
    screenResolution = None

    def setUseragent(self, userAgent):
        self.userAgent = userAgent

    def getUseragent(self):
        return self.userAgent

    def getScreenResolution(self):
        return self.screenResolution

    def setScreenResolution(self, screenWidth, screenHeight):
        self.screenResolution = screenWidth, screenHeight
