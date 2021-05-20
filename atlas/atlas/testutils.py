"""Atlas test utils."""
# pylint: disable=C0103,C0412,W0201,E0213,C0202,R1725,W0106

import os
import re
import signal
import time
from importlib import import_module
from pathlib import Path

import coverage
from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.db import connections
from django.http import HttpRequest
from django.test import Client, TestCase
from django.test.testcases import LiveServerThread
from selenium.common.exceptions import NoSuchElementException, WebDriverException


class AtlasTestCase(TestCase):
    """Atlas base test case."""

    fixtures = [
        "userroles.yaml",
        "rolepermissions.yaml",
        "estimatedrunfrequency.yaml",
        "financialimpact.yaml",
        "fragility.yaml",
        "fragilitytag.yaml",
        "maintenancelogstatus.yaml",
        "organizationalvalue.yaml",
        "projectmilestonefrequency.yaml",
        "reporttypes.yaml",
        "rolepermissionlinks.yaml",
        "rolepermissions.yaml",
        "seed.yaml",
        "strategicimportance.yaml",
        "userroles.yaml",
        "test.yaml",
    ]

    def setUp(self):
        """Set up live server test."""
        super().setUp()
        self.client = Client()

    def login(self):
        """Login as user."""
        assert self.client.login(username="user@user.user", password="123")

    def login_admin(self):
        """Login as admin."""
        assert self.client.login(username="admin@admin.admin", password="123")

    def verify_body_links(self, html):
        """Verify links links in  div.body-main."""
        links = (
            BeautifulSoup(html, features="html5lib")
            .select_one("div.body-main")
            .find_all("a", href=True)
        )

        for a_link in links:
            link = a_link.get("href")
            # all links must start with either http, / or #.
            self.assertTrue(re.search(r"^(?:http\:\/\/|\/|#)", link))
            # links starting with a / must be reachable.
            response = self.client.get(link, follow=False)
            self.assertEqual(response.status_code, 200)


class SeleniumWrapper:
    """Wraps the test for each browser.

    https://github.com/aptiko/django-selenium-clean/blob/master/LICENSE.txt
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Set up new instance."""
        if not cls._instance:
            cls._instance = super(SeleniumWrapper, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        """Initialize web driver if there are settings."""
        SELENIUM_WEBDRIVERS = getattr(settings, "SELENIUM_WEBDRIVERS", {})  # noqa: N806
        if not SELENIUM_WEBDRIVERS:
            return

        driver_id = os.environ.get("SELENIUM_WEBDRIVER", "default")
        driver = SELENIUM_WEBDRIVERS[driver_id]
        d_callable = driver["callable"]
        args = driver["args"]
        kwargs = driver["kwargs"]
        self.driver = d_callable(*args, **kwargs)

    def __getattr__(self, name):
        """Get attribute."""
        return getattr(self.driver, name)

    def __setattr__(self, name, value):
        """Set attribute."""
        if name == "driver":
            super(SeleniumWrapper, self).__setattr__(name, value)
        else:
            setattr(self.driver, name, value)

    def __bool__(self):
        """Return bool."""
        return bool(self.driver)

    __nonzero__ = __bool__  # Python 2 compatibility

    def login(self, **credentials):
        """Login to app.

        Sets selenium to appear as if a user has successfully signed in.
        Returns True if signin is possible; False if the provided
        credentials are incorrect, or the user is inactive, or if the
        sessions framework is not available.
        The code is based on django.test.client.Client.login.
        """
        from django.contrib.auth import authenticate, login

        # Visit the home page to ensure the cookie gets the proper domain
        self.get(self.live_server_url)

        user = authenticate(**credentials)
        if not (
            user
            and user.is_active
            and "django.contrib.sessions" in settings.INSTALLED_APPS
        ):
            return False

        engine = import_module(settings.SESSION_ENGINE)

        # Create a fake request to store login details.
        request = HttpRequest()
        request.session = engine.SessionStore()
        login(request, user)

        # Save the session values.
        request.session.save()

        # Set the cookie to represent the session.
        cookie_data = {
            "name": settings.SESSION_COOKIE_NAME,
            "value": request.session.session_key,
            "max-age": None,
            "path": "/",
            "secure": settings.SESSION_COOKIE_SECURE or False,
            "expires": None,
        }
        self.add_cookie(cookie_data)

        return True

    def logout(self):
        """Logout from app.

        Removes the authenticated user's cookies and session object.
        Causes the authenticated user to be logged out.
        """
        session = import_module(settings.SESSION_ENGINE).SessionStore()
        session_cookie = self.get_cookie(settings.SESSION_COOKIE_NAME)
        if session_cookie:
            session.delete(session_key=session_cookie["value"])
            self.delete_cookie(settings.SESSION_COOKIE_NAME)

    def squit(self):
        """Exit browser."""
        # The way to exit the browser is selenium.driver.quit(), however we
        # exit PhantomJS differently because of
        # https://github.com/SeleniumHQ/selenium/issues/767
        if self.driver.capabilities["browserName"] == "phantomjs":
            self.driver.service.process.send_signal(signal.SIGTERM)
        else:
            self.driver.quit()


class AtlasBrowserTestCase(TestCase):
    """Selenium test case.

    Most code is from django.test.testcase as we cannot use the "normal"
    live server test case with a preexisting database.

    Other parts of code are use from
    https://github.com/aptiko/django-selenium-clean/blob/master/LICENSE.txt
    """

    fixtures = [
        "userroles.yaml",
        "rolepermissions.yaml",
        "estimatedrunfrequency.yaml",
        "financialimpact.yaml",
        "fragility.yaml",
        "fragilitytag.yaml",
        "maintenancelogstatus.yaml",
        "organizationalvalue.yaml",
        "projectmilestonefrequency.yaml",
        "reporttypes.yaml",
        "rolepermissionlinks.yaml",
        "rolepermissions.yaml",
        "seed.yaml",
        "strategicimportance.yaml",
        "userroles.yaml",
        "test.yaml",
    ]

    host = "localhost"
    port = 0
    server_thread_class = LiveServerThread
    static_handler = StaticFilesHandler

    def setUp(self):
        """Set up live server test."""
        super().setUp()

        # create a live server connection
        rcfile = str(Path(__file__).parent.parent / ".coveragerc")

        self.cov = coverage.Coverage(config_file=rcfile, concurrency="thread")
        self.cov.start()

        connections_override = {}
        for conn in connections.all():
            # If using in-memory sqlite databases, pass the connections to
            # the server thread.
            if conn.vendor == "sqlite" and conn.is_in_memory_db():
                # Explicitly enable thread-shareability for this connection
                conn.inc_thread_sharing()
                connections_override[conn.alias] = conn

        self.server_thread = self._create_server_thread(connections_override)
        self.server_thread.daemon = True
        self.server_thread.start()

        # Wait for the live server to be ready
        self.server_thread.is_ready.wait()
        if self.server_thread.error:
            # Clean up behind ourselves, since tearDownClass won't get called in
            # case of errors.
            self._tearDownInternal()
            raise self.server_thread.error

        self.selenium = SeleniumWrapper()

        self.selenium.live_server_url = self.live_server_url()

    def login(self):
        """Login function for dev auth."""
        self.selenium.get(self.url(""))
        self.assertEqual(
            "Atlas Dev",
            self.selenium.find_element_by_xpath('//h2[@class="login-ttl"]').text,
        )
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys("user@user.user")

        self.selenium.find_element_by_xpath('//button[text()="Log In"]').click()
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath('//h2[@class="login-ttl"]').text

    def login_admin(self):
        """Login function for dev auth."""
        self.selenium.get(self.url(""))
        self.assertEqual(
            "Atlas Dev",
            self.selenium.find_element_by_xpath('//h2[@class="login-ttl"]').text,
        )
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys("admin@admin.admin")

        self.selenium.find_element_by_xpath('//button[text()="Log In"]').click()
        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath('//h2[@class="login-ttl"]').text

    def live_server_url(self):
        """Return live server url."""
        return "http://{}:{}".format(self.host, self.server_thread.port)

    def url(self, addr):
        """Build url for testing.

        Hopefully avoid needing to repeat live_server_url constantly.
        """
        return "http://{}:{}{}".format(self.host, self.server_thread.port, addr)

    def _create_server_thread(self, connections_override):
        return self.server_thread_class(
            self.host,
            self.static_handler,
            connections_override=connections_override,
            port=self.port,
        )

    def _tearDownInternal(self):
        # There may not be a 'server_thread' attribute if setUpClass() for some
        # reasons has raised an exception.
        if hasattr(self, "server_thread"):
            # Terminate the live server's thread
            self.server_thread.terminate()

            # Restore sqlite in-memory database connections' non-shareability.
            for conn in self.server_thread.connections_override.values():
                conn.dec_thread_sharing()

            # self._live_server_modified_settings.disable()
            super().tearDown()

    def tearDown(self):
        """Cleanup leftovers from testing."""
        self.selenium.squit()
        super().tearDown()
        self.cov.stop()
        self.cov.save()

    def __call__(self, result=None):
        """Allow testing in multiple screen sizes."""
        if hasattr(self, "selenium"):
            for width in getattr(settings, "SELENIUM_WIDTHS", [1024]):
                i = 0
                while True:
                    try:
                        self.selenium.set_window_size(width, 1024)
                        break
                    except WebDriverException:
                        if i >= 10:
                            raise
                        i += 1
                        time.sleep(0.5)
        return super(AtlasBrowserTestCase, self).__call__(result)
