"""Browserstack config.

Imports the standard test config and adds a test runner.
"""

from .test import *

BROWSERSTACK_CAPS = [
    {
        "os_version": "10",
        "os": "Windows",
        "browser": "chrome",
        "browser_version": "latest",
    },
    # {
    #     "realMobile": "true",
    #     "browserName": "android",
    #     "device": "Samsung Galaxy S21 Ultra",
    #     "os_version": "11.0",
    # },
    # {
    #     "os_version": "Big Sur",
    #     "os": "OS X",
    #     "browser": "safari",
    #     "browser_version": "latest",
    # },
]

TEST_RUNNER = "atlas.browserstack_runner.BrowserStackDiscoverRunner"
