//function getScreenshot(domain) {
//    var screenPath = screenshotsPath + domain + '.png';
//    page.clipRect = { top: 0, left: 0, width: 1366, height: 768 };
//    page.viewportSize = { width: 1366, height: 768 };
//    page.settings.userAgent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/30.0.1599.114 Chrome/30.0.1599.114 Safari/537.36';
//    page.settings.resourceTimeout = 10000;
//    page.onResourceTimeout = function(e) {
//        console.log(domain+' timeout');
//    };
//    page.open('http://'+domain+'/', function(status) {
//        if (status != 'success') {
//            console.log('Can\'t open '+domain);
//        } else {
//            page.evaluate(function() {
//                var style = document.createElement('style'),
//                    text = document.createTextNode('BODY { background-color: #fff }');
//                style.setAttribute('type', 'text/css');
//                style.appendChild(text);
//                document.head.insertBefore(style, document.head.firstChild);
//            });
//            takeScreenshot(page, 1366, 768);
//        }
//    });
//}

function fixPageBackground(page) {
    page.evaluate(function() {
        var style = document.createElement('style'),
            text = document.createTextNode('BODY { background-color: #fff }');
        style.setAttribute('type', 'text/css');
        style.appendChild(text);
        document.head.insertBefore(style, document.head.firstChild);
    });
}

function updateTakenScreens() {
    takenScreens += 1;
    console.log('Rendered! Screenshots: ' + takenScreens);
    if (takenScreens >= devices.length) {
        takenScreens = 0;
        //phantom.exit();
    }
}

function takeScreenshot(device) {
    if (usingPage == true) {
        setTimeout(function () {
            takeScreenshot(device);
        }, 500);
        return;
    }
    var screenPath = screenshotsPath + domain + '_' + device.getDeviceName() + '.png';
    usingPage = true;
    page.clipRect = { top: 0, left: 0, width: device.getWidth(), height: device.getHeight() };
    page.viewportSize = { width: device.getWidth(), height: device.getHeight() };

    page.settings.userAgent = device.getUserAgent()
    page.settings.resourceTimeout = 10000;
    page.onResourceTimeout = function(e) {
        console.log(domain + ' timeout for device ' + device.getDeviceName());
        updateTakenScreens();
    };
    page.open('http://'+domain+'/', function(status) {
        if (status != 'success') {
            console.log('Can\'t open '+domain);
        } else {
            fixPageBackground(page);
            console.log('Rendering ' + device.getDeviceName() + ' screenshot..');
            page.render(screenPath);
            //page.open(serverUrl + 'resize?screenshotPath='+screenPath);
        }
        updateTakenScreens();
        usingPage = false;
    });
}

function takeScreenshots() {
    takingScreenshots = true;
    takeScreenshot(iPhone);
    takeScreenshot(iPad);
    takeScreenshot(laptop);
}

function readServerResponse() {
    if (usingPage == true) {
        setTimeout("readServerResponse", 500);
        return;
    }
    usingPage = true;
    page.settings.resourceTimeout = 10000;
    page.onResourceTimeout = function(e) {
        console.log('Server timeout.');
    };
    page.open(serverUrl + 'get_domain', function(status) {
        if (status != 'success') {
            //http request to the server failed
            console.log('ERROR: Communication to the server failed');
        } else {
            var serverResponse = page.evaluate(function () {
                return document.body.innerHTML
            });
            if (serverResponse == 'empty') {
                console.log('No domains left in the queue.');
            } else {
                domain = serverResponse;
                console.log('Taking screenshot of ' + domain);
                takeScreenshots(domain);
            }
        }
        usingPage = false;
    });
}

function Device() {
    this.width = 0;
    this.height = 0;
    this.userAgent = '';
    this.deviceName = '';

    this.setDeviceName = function (name) {
        this.deviceName = name;
    }

    this.getDeviceName = function () {
        return this.deviceName;
    }

    this.setWidth = function (width) {
        this.width = width;
    }

    this.getWidth = function () {
        return this.width;
    }

    this.setHeight = function (height) {
        this.height = height;
    }

    this.getHeight = function () {
        return this.height;
    }

    this.setUserAgent = function (userAgent) {
        this.userAgent = userAgent;
    }

    this.getUserAgent = function () {
        return this.userAgent;
    }
}

var takenScreens = 0;
var usingPage = false;
var page = require('webpage').create();
var devices = new Array();

var iPhone = new Device();
iPhone.setDeviceName('iPhone');
iPhone.setWidth(640);
iPhone.setHeight(1136);
iPhone.setUserAgent('Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3');
devices.push(iPhone);

var iPad = new Device();
iPad.setDeviceName('iPad');
iPad.setWidth(1024);
iPad.setHeight(768);
iPad.setUserAgent('Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B176 Safari/7534.48.3');
devices.push(iPad);

var laptop = new Device();
laptop.setDeviceName('Laptop');
laptop.setWidth(1280);
laptop.setHeight(768);
laptop.setUserAgent('Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/30.0.1599.114 Chrome/30.0.1599.114 Safari/537.36');
devices.push(laptop);

var serverUrl = 'http://0.0.0.0:8088/';
var screenshotsPath = 'screens/';

setInterval(readServerResponse, 2000);
