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
import re

from selenium.webdriver.common.keys import Keys

from atlas.testutils import AtlasBrowserStackTestCase


class IndexTestCase(AtlasBrowserStackTestCase):
    def test_all_terms(self):
        """Check all terms page."""
        self.login()

        # open dropdown for links
        self.selenium.find_element_by_css_selector("#nav-drop-objects").click()

        # click on terms
        self.selenium.find_element_by_link_text("Terms").click()

        # verify no logs
        # self.assertEqual(self.log_count(), 0)

        # verify correct url
        self.assertIn("/terms", self.selenium.current_url)

        # verify terms loaded
        self.assertEqual(
            self.selenium.find_element_by_css_selector(".pageTitle-head").text, "Terms"
        )

    def test_term_page(self):
        """Open a term."""
        self.login()

        # open dropdown for links
        self.selenium.find_element_by_css_selector("#nav-drop-objects").click()

        # click on terms
        self.selenium.find_element_by_link_text("Terms").click()

        # open first term dropdown
        self.selenium.find_element_by_css_selector(
            'h4.drop[data-toggle="clps"]'
        ).click()

        # open the term
        self.selenium.find_element_by_css_selector("div.clps-o a.drop-link").click()

        # check link
        self.assertTrue(bool(re.match(r".+/terms/\d+", self.selenium.current_url)))

    def test_term_permissions(self):
        """Check that a nobody cannot create/edit terms."""
        self.login()

        self.selenium.get(self.url("/terms"))

        # new term button should not be there
        self.assertRaises(
            self.selenium.find_element_by_css_selector("a.nav-link.new").click()
        )

        # new, edit and delete buttons should not be there
        self.selenium.get(self.url("/terms/1"))

        self.assertRaises(
            self.selenium.find_element_by_css_selector("a.nav-link.new").click()
        )
        self.assertRaises(
            self.selenium.find_element_by_css_selector("a.nav-link.edit").click()
        )
        self.assertRaises(
            self.selenium.find_element_by_css_selector("a.nav-link.delete").click()
        )

    def test_old_term_links(self):
        """Check old term links."""
        self.login()
        self.selenium.get(self.url("/terms?id=1"))
        # check link
        self.assertTrue(bool(re.match(r".+/terms/1", self.selenium.current_url)))

    def test_non_existing_term(self):
        """Check terms that don't exist."""
        self.login()
        self.selenium.get(self.url("/terms/99999999"))
        self.assertTrue(bool(re.match(r".+/terms/?$", self.selenium.current_url)))

    def test_create_term_from_all_terms(self):
        """Create a term from the all terms page."""
        self.login("admin@admin.admin")
        self.selenium.get(self.url("/terms"))

        # open modal
        self.selenium.find_element_by_css_selector("a.nav-link.new").click()

        # fill in form name
        self.selenium.find_element_by_css_selector(
            'form[action="/terms/new"] input[name="name"]'
        ).send_keys("selenium test term")

        # tab to form summary
        self.selenium.find_element_by_css_selector(
            'form[action="/terms/new"] input[name="name"]'
        ).send_keys(Keys.TAB * 5)

        self.selenium.find_element_by_css_selector(
            'div.editor.loaded[data-inputid="summary"] div[role="presentation"]'
        ).send_keys("nice summary!")

        # verify summary was parsed
        self.assertEqual(
            self.selenium.find_element_by_css_selector(
                'div.editor.loaded[data-inputid="summary"] div.editor-liveEditorPrev'
            ).text,
            "nice summary!",
        )

        # save term
        save_button = self.selenium.find_element_by_css_selector(
            'form[action="/terms/new"] button.editor-save'
        )
        self.selenium.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        save_button.click()

        # delete term

        # verify no logs
        # self.assertEqual(self.log_count(), 0)


# for log in driver.get_log('browser'): print(log)
