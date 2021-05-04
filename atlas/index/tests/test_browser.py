"""Atlas Index Selenium tests."""
# pylint: disable=C0115,W0106,C0103

from atlas.testutils import AtlasBrowserTestCase


class IndexTestCase(AtlasBrowserTestCase):

    fixtures = ["demo.yaml"]

    def test_index(self):
        """Verify home page is reachable."""
        self.selenium.get(self.url(""))

    def test_login(self):
        """Verify that we can login."""
        self.selenium.login(username=self.user.email)
        self.selenium.logout()

    def test_test_login(self):
        """Verify that dev login method works."""
        self.login()
