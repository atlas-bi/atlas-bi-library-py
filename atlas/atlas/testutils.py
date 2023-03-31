# type: ignore
"""Atlas test utils."""
# pylint: disable=C0103,C0412,W0201,E0213,C0202,R1725,W0106

import os
import re

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import Client, TestCase
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


class AtlasTestCase(TestCase):
    """Atlas base test case."""

    fixtures = [
        # "userroles.yaml",
        # "rolepermissions.yaml",
        # "runfrequency.yaml",
        # "financialimpact.yaml",
        # "fragility.yaml",
        # "fragilitytag.yaml",
        # "maintenancelogstatus.yaml",
        # "organizationalvalue.yaml",
        # "reporttypes.yaml",
        # "rolepermissionlinks.yaml",
        # "rolepermissions.yaml",
        # "strategicimportance.yaml",
        # "userroles.yaml",
        "initial.yaml",
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


class AtlasBrowserStackTestCase(StaticLiveServerTestCase):
    """Browserstack test case.

    Most code is from django.test.testcase as we cannot use the "normal"
    live server test case with a preexisting database.
    """

    # don't add the "seed.yaml" as contenttypes are auto added.
    fixtures = [
        # "userroles.yaml",
        # "rolepermissions.yaml",
        # "runfrequency.yaml",
        # "financialimpact.yaml",
        # "fragility.yaml",
        # "fragilitytag.yaml",
        # "maintenancelogstatus.yaml",
        # "organizationalvalue.yaml",
        # "projectmilestonefrequency.yaml",
        # "reporttypes.yaml",
        # "rolepermissionlinks.yaml",
        # "rolepermissions.yaml",
        # "strategicimportance.yaml",
        # "userroles.yaml",
        "initial.yml"
        "test.yaml",
    ]

    @classmethod
    def setUpClass(cls):
        """Set up live server test."""
        super().setUpClass()

        user_name = os.environ["BROWSERSTACK_USERNAME"]
        access_key = os.environ["BROWSERSTACK_ACCESS_KEY"]
        build_name = os.environ["BROWSERSTACK_BUILD_NAME"]
        project_name = os.environ["BROWSERSTACK_PROJECT_NAME"]

        desired_cap = getattr(settings, "WEBDRIVER", {})
        desired_cap["build"] = build_name
        desired_cap["project"] = project_name
        desired_cap["browserstack.local"] = "true"
        desired_cap["browserstack.console"] = "errors"
        desired_cap["browserstack.networkLogs"] = "true"

        cls.selenium = webdriver.Remote(
            command_executor="https://"
            + user_name
            + ":"
            + access_key
            + "@hub-cloud.browserstack.com/wd/hub",
            desired_capabilities=desired_cap,
        )

        # implicit wait throws a w3c error in some combinations
        # not edge
        # not Windows 10 + chrome
        # not osx + chrome
        if not (
            desired_cap.get("browser", "other") == "edge"
            or (
                desired_cap.get("browser", "other") == "chrome"
                and desired_cap.get("os_version", "other") == "10"
                and desired_cap.get("os", "other") == "Windows"
            )
            or (
                desired_cap.get("browser", "other") == "chrome"
                and desired_cap.get("os", "other") == "OS X"
            )
        ):
            cls.selenium.implicitly_wait(10)
        else:
            cls.selenium.set_page_load_timeout(10)

    def log_count(self):
        """Check for error logs."""
        logs = []
        for log in self.selenium.get_log("browser"):
            if log["level"] in ["ERROR", "WARNING", "SEVERE"]:
                logs.append(log)

        if len(logs) > 0:
            # pylint: disable=C0301
            self.selenium.execute_script(
                'browserstack_executor: {"action": "setSessionStatus", "arguments": {"status":"failed", "reason": "console errors"}}'  # noqa: E501
            )

        print(logs)  # noqa: T001
        return len(logs)

    def login(self, username="user@user.user"):
        """Login function for dev auth."""
        self.assertTrue(self.client.login(username=username))

        cookie = self.client.cookies["sessionid"]
        self.selenium.get(
            self.live_server_url
        )  # visit page in the site domain so the page accepts the cookie
        self.selenium.add_cookie(
            {
                "name": "sessionid",
                "value": cookie.value,
                "secure": False,
                "path": "/",
                "expires": None,
                "max-age": None,
            }
        )

        # get home page and make sure we are logged in/
        self.selenium.get(self.live_server_url)

        with self.assertRaises(NoSuchElementException):
            self.selenium.find_element_by_xpath('//h2[@class="login-ttl"]').text

        return True

    def url(self, addr):
        """Build url for testing.

        Hopefully avoid needing to repeat live_server_url constantly.
        """
        return "{}{}".format(self.live_server_url, addr)

    @classmethod
    def tearDownClass(cls):
        """Class cleanup."""
        cls.selenium.quit()
        super().tearDownClass()
