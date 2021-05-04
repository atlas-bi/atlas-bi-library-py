"""Atlas Initiative tests."""
# pylint: disable=C0115,C0103

from atlas.testutils import AtlasTestCase
from index.models import Initiatives


class InitiativeTestCase(AtlasTestCase):
    """Setup tests.

    A custom test setup is used (atlas/custom_test_runner.py).
    We need to declare what db's are involved in testing.

    default is required.
    """

    # pre-login tests.
    # verify that all pages redirect to login screen.

    def test_login_initiatives(self):
        """Check that users are sent from ``/initiatives`` to login page."""
        response = self.client.get("/initiatives/", follow=False)
        self.assertEqual(response.url, "/accounts/login/?next=/initiatives/")
        self.assertEqual(response.status_code, 302)

    def test_login_initiative(self):
        """Check that users are sent from ``/initiatives/%s`` to login page."""
        initiative = Initiatives.objects.first()
        response = self.client.get(
            "/initiatives/%s" % initiative.initiative_id, follow=False
        )
        self.assertEqual(
            response.url,
            "/accounts/login/?next=/initiatives/%s" % initiative.initiative_id,
        )
        self.assertEqual(response.status_code, 302)

    # logged in tests.

    def test_invalid_initiative(self):
        """Check that invalid initiatives redirect."""
        # find an initiative that doesn't exist.
        self.login()
        initiative = Initiatives.objects.order_by("initiative_id").last()

        assert (
            self.client.get(
                "/initiatives/%s" % (initiative.initiative_id + 1)
            ).status_code
            == 302
        )

    def test_valid_initiative(self):
        """Check that valid initiatives are viewable."""
        self.login()
        initiative = Initiatives.objects.first()
        response = self.client.get("/initiatives/%s" % initiative.initiative_id)

        self.assertEqual(response.status_code, 200)

        self.verify_body_links(response.content)

    def test_old_urls(self):
        """Check that atlas v1 urls are viewable."""
        self.login()
        initiative = Initiatives.objects.first()
        response = self.client.get(
            "/initiatives?id=%s" % initiative.initiative_id, follow=True
        )
        assert (
            response.redirect_chain[-1][0]
            == "/initiatives/%s" % initiative.initiative_id
        )
        assert (
            self.client.get(
                "/initiatives?id=%s" % initiative.initiative_id, follow=True
            ).status_code
            == 200
        )

    def test_all_initiatives(self):
        """Check that "all initiatives" page is viewable."""
        self.login()
        response = self.client.get("/initiatives", follow=True)
        assert response.status_code == 200

        self.verify_body_links(response.content)
