#!/usr/bin/env python
from selenium import webdriver
from pyshotx import Device, Browser


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
