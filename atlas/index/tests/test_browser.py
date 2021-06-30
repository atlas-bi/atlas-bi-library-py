"""Atlas Index Selenium tests."""
# pylint: disable=C0115,W0106,C0103

from atlas.testutils import AtlasBrowserStackTestCase


class IndexTestCase(AtlasBrowserStackTestCase):
    def test_index(self):
        """Verify home page is reachable."""
        self.selenium.get(self.url(""))

    def test_test_login(self):
        """Verify that dev login method works."""
        self.login()


# for log in driver.get_log('browser'): print(log)
