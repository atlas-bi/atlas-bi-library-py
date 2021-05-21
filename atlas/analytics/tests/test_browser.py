"""Atlas Index Selenium tests."""
# pylint: disable=C0115,W0106,C0103

from atlas.testutils import AtlasBrowserStackTestCase


class IndexTestCase(AtlasBrowserStackTestCase):
    def test_index_user(self):
        """Basic users should be not authorized."""
        self.selenium.get(self.url(""))
        self.login(username="user@user.user")
        self.selenium.get(self.url("/analytics/"))

    def test_two(self):
        self.selenium.get(self.url("/analytics/"))
