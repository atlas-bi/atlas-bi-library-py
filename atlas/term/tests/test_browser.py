"""Atlas Term Selenium tests.

Run test for this app with::

    # or set these in atlas/settings/test_cust.py
    export BROWSERSTACK_USERNAME=; \
    export BROWSERSTACK_ACCESS_KEY=; \
    export BROWSERSTACK_BUILD_NAME="local"; \
    export BROWSERSTACK_PROJECT_NAME="Atlas-Py"; \

    poetry run coverage erase; \
    poetry run coverage run -p manage.py \
        test term/ --no-input --pattern="test_browser.py" --settings atlas.settings.test_browser; \
    poetry run coverage combine; \
    poetry run coverage report --include "term*" -m

"""
# pylint: disable=C0115,W0106,C0103

from atlas.testutils import AtlasBrowserStackTestCase


class IndexTestCase(AtlasBrowserStackTestCase):
    def test_index(self):
        """Verify home page is reachable."""
        self.selenium.get(self.url(""))

    def test_test_login(self):
        """Verify that dev login method works."""
        self.login()

    def test_all_terms(self):
        self.login()
        self.selenium.get(self.url("/terms"))
        self.assertEqual(self.logs(), [])


# for log in driver.get_log('browser'): print(log)
