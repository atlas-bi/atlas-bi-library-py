"""Atlas User tests."""
# pylint: disable=C0115,C0103
from atlas.testutils import AtlasTestCase


class UserTestCase(AtlasTestCase):
    def test_video_preference_without_login(self):
        """Check that users are sent to login page."""
        response = self.client.get("/user/preference/video/1", follow=False)
        self.assertEqual(response.url, "/accounts/login/?next=/user/preference/video/1")
        self.assertEqual(response.status_code, 302)

    def test_video_preference_with_login(self):
        """Check that homepage is accessible after login."""
        self.login()
        response = self.client.get("/user/preference/video/1")
        self.assertEqual(response.status_code, 200)
