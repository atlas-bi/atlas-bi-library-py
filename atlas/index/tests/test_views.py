"""Atlas Index tests."""
# pylint: disable=C0115,C0103
from atlas.testutils import AtlasTestCase


class IndexTestCase(AtlasTestCase):
    def test_homepage_without_login(self):
        """Check that users are sent to login page."""
        response = self.client.get("/", follow=False)
        self.assertEqual(response.url, "/accounts/login/?next=/")
        self.assertEqual(response.status_code, 302)

    def test_homepage_with_bad_login(self):
        """Check that bad users are asked to login again."""
        self.client.login(username="bad_user@user.user", password="123")
        response = self.client.get("/", follow=False)
        self.assertEqual(response.status_code, 302)

    def test_homepage_with_login(self):
        """Check that homepage is accessible after login."""
        self.login()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
