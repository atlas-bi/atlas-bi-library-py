"""Browserstack config.

Imports the standard test config and adds a test runner.
"""
import contextlib

from .test import *

BROWSERSTACK_CAPS = []

# windows 10 + chrome
BROWSERSTACK_CAPS.append(
    {
        "os_version": "10",
        "os": "Windows",
        "browser": "chrome",
        "browser_version": "latest",
        "resolution": "2048x1536",
    }
)

# windows 10 + edge
BROWSERSTACK_CAPS.append(
    {
        "os_version": "10",
        "os": "Windows",
        "browser": "edge",
        "browser_version": "latest",
    }
)

# windows 10 + firefox
BROWSERSTACK_CAPS.append(
    {
        "os_version": "10",
        "os": "Windows",
        "browser": "firefox",
        "browser_version": "90.0",
    }
)

# windows 10 + IE 11 🤮
BROWSERSTACK_CAPS.append(
    {
        "os_version": "10",
        "os": "Windows",
        "browser": "ie",
        "browser_version": "11.0",
    }
)

# windows 7 + IE 11 🤮
BROWSERSTACK_CAPS.append(
    {
        "os_version": "7",
        "os": "Windows",
        "browser": "ie",
        "browser_version": "11.0",
    }
)

# osx Big Sur + safari
BROWSERSTACK_CAPS.append(
    {
        "os_version": "Big Sur",
        "os": "OS X",
        "browser": "safari",
        "browser_version": "latest",
    }
)

# osx Big Sur + chrome
BROWSERSTACK_CAPS.append(
    {
        "os_version": "Big Sur",
        "os": "OS X",
        "browser": "chrome",
        "browser_version": "latest",
    }
)


# iOS 12 max
BROWSERSTACK_CAPS.append(
    {
        "realMobile": "true",
        "os_version": "14",
        "browserName": "iOS",
        "device": "iPhone 12 Pro Max",
    }
)

# iOS 8
BROWSERSTACK_CAPS.append(
    {
        "realMobile": "true",
        "os_version": "13",
        "browserName": "iOS",
        "device": "iPhone 8",
    }
)

# iOS 7
BROWSERSTACK_CAPS.append(
    {
        "realMobile": "true",
        "os_version": "12",
        "browserName": "iOS",
        "device": "iPhone 7",
    }
)

# iOS Ipad Air 4
BROWSERSTACK_CAPS.append(
    {
        "realMobile": "true",
        "os_version": "14",
        "browserName": "iOS",
        "device": "iPad Air 4",
    }
)

# iOS Ipad 8th
BROWSERSTACK_CAPS.append(
    {
        "realMobile": "true",
        "os_version": "14",
        "browserName": "iOS",
        "device": "iPad 8th",
    }
)

# android Galaxy S21
BROWSERSTACK_CAPS.append(
    {
        "realMobile": "true",
        "os_version": "11.0",
        "browserName": "android",
        "device": "Samsung Galaxy S21",
    }
)

# android Galaxy S10
BROWSERSTACK_CAPS.append(
    {
        "realMobile": "true",
        "os_version": "9.0",
        "browserName": "android",
        "device": "Samsung Galaxy S10",
    }
)

# android Google Pixel 5
BROWSERSTACK_CAPS.append(
    {
        "realMobile": "true",
        "os_version": "11.0",
        "browserName": "android",
        "device": "Google Pixel 5",
    }
)

# android Galaxy Tab S7
BROWSERSTACK_CAPS.append(
    {
        "realMobile": "true",
        "os_version": "10.0",
        "browserName": "android",
        "device": "Samsung Galaxy Tab S7",
    }
)

TEST_RUNNER = "atlas.browserstack_runner.BrowserStackDiscoverRunner"

# import custom overrides
with contextlib.suppress(ImportError):
    from .test_browser_cust import *
