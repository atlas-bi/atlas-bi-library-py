"""Atlas Index Selenium tests."""
# pylint: disable=C0115,W0106,C0103

from atlas.testutils import AtlasBrowserTestCase


class IndexTestCase(AtlasBrowserTestCase):
    def test_index_user(self):
        """Basic users should be not authorized."""
        self.selenium.get(self.url(""))
        self.login()
        self.selenium.get(self.url("/analytics/"))
