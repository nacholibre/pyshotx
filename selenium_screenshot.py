#!/usr/bin/env python
from selenium import webdriver
#   xvfb-run -s "-screen 0 1024x768x24" python getschreenshot.py test.html


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


if __name__ == '__main__':
    iphone = Device()
    iphone.setUseragent('Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS'
                        'X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) '
                        'Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
    iphone.setScreenResolution(640, 1136)

    ipad = Device()
    ipad.setUseragent('Mozilla/5.0(iPad; U; CPU OS 4_3 like Mac OS'
                      'X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) '
                      'Version/5.0.2 Mobile/8F191 Safari/6533.18.5')
    ipad.setScreenResolution(1536, 2048)

    browser = Browser(webdriver.Chrome)
    browser.setDevice(iphone)
    browser.get('http://dir.bg')
    browser.saveScreenshot('screenie.png')
    browser.quit()
