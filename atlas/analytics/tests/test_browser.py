"""Atlas Index Selenium tests.

Run test for this app with::

    # or set these in atlas/settings/test_cust.py
    export BROWSERSTACK_USERNAME=; \
    export BROWSERSTACK_ACCESS_KEY=; \
    export BROWSERSTACK_BUILD_NAME="local"; \
    export BROWSERSTACK_PROJECT_NAME="Atlas-Py"; \

    poetry run coverage erase; \
    poetry run coverage run -p manage.py \
        test analytics/ --no-input --pattern="test_browser.py" --settings atlas.settings.test_browser; \
    poetry run coverage combine; \
    poetry run coverage report --include "analytics*" -m
"""
# pylint: disable=C0115,W0106,C0103

from atlas.testutils import AtlasBrowserStackTestCase


class IndexTestCase(AtlasBrowserStackTestCase):
    def test_index_user(self):
        """Basic users should be not authorized."""
        self.selenium.get(self.url(""))
        self.login()
        self.selenium.get(self.url("/analytics/"))

    def test_two(self):
        self.selenium.get(self.url("/analytics/"))
