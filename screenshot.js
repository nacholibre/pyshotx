function getScreenshot(domain) {
    var screenPath = screenshotsPath + domain + '.png';
    var page = require('webpage').create();
    page.clipRect = { top: 0, left: 0, width: 1366, height: 768 };
    page.viewportSize = { width: 1366, height: 768 };
    page.settings.userAgent = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/30.0.1599.114 Chrome/30.0.1599.114 Safari/537.36';
    page.settings.resourceTimeout = 10000;
    page.onResourceTimeout = function(e) {
        console.log(domain+' timeout');
    };
    page.open('http://'+domain+'/', function() {
        page.evaluate(function() {
            var style = document.createElement('style'),
                text = document.createTextNode('BODY { background-color: #fff }');
            style.setAttribute('type', 'text/css');
            style.appendChild(text);
            document.head.insertBefore(style, document.head.firstChild);
        });
        page.render(screenPath);
        page.open(serverUrl + 'resize?screenshotPath='+screenPath);
    });
}

function getDomain() {
    var page = require('webpage').create();
    page.open(serverUrl + 'getDomain', function(status) {
        if (status != 'success') {
            console.log('Communication to the server failed');
            phantom.exit();
        } else {
            var domain = page.evaluate(function () {
                return document.body.innerHTML
            });
            if (domain == 'empty') {
                console.log('No domains left in the queue.');
            } else {
                getScreenshot(domain);
            }
        }
    });
}

var serverUrl = 'http://0.0.0.0:8088/';
var screenshotsPath = '/home/nacholibre/nacho_tarantula/screenshots/screens/';

setInterval(getDomain, 2000);
