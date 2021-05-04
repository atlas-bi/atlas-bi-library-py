"""Term app tests."""
from atlas.testutils import AtlasTestCase
from index.models import Terms

# pylint: disable=C0103,W0105,C0115


class TermTestCase(AtlasTestCase):

    # pre-login tests.
    # verify that all pages redirect to login screen.

    def test_login_terms(self):
        """Check that users are sent from ``/terms`` to login page."""
        response = self.client.get("/terms/", follow=False)
        self.assertEqual(response.url, "/accounts/login/?next=/terms/")
        self.assertEqual(response.status_code, 302)

    def test_login_term(self):
        """Check that users are sent from ``/terms/%s`` to login page."""
        term = Terms.objects.first()
        response = self.client.get("/terms/%s" % term.term_id, follow=False)
        self.assertEqual(response.url, "/accounts/login/?next=/terms/%s" % term.term_id)
        self.assertEqual(response.status_code, 302)

    def test_login_comments(self):
        """Check that users are sent from ``/terms/%s/comments`` to login page."""
        term = Terms.objects.first()
        response = self.client.get("/terms/%s/comments" % term.term_id, follow=False)
        self.assertEqual(
            response.url, "/accounts/login/?next=/terms/%s/comments" % term.term_id
        )
        self.assertEqual(response.status_code, 302)

    # logged in tests.

    def test_invalid_term(self):
        """Check that invalid terms redirect."""
        self.login()
        # find a term that doesn't exist.
        term = Terms.objects.order_by("term_id").last()

        assert self.client.get("/terms/%s" % (term.term_id + 1)).status_code == 302

    def test_valid_term(self):
        """Check that valid terms are viewable."""
        self.login()
        term = Terms.objects.first()
        assert self.client.get("/terms/%s" % term.term_id).status_code == 200

    def test_old_urls(self):
        """Check that atlas v1 urls are viewable."""
        self.login()
        term = Terms.objects.first()
        response = self.client.get("/terms?id=%s" % term.term_id, follow=True)
        assert response.redirect_chain[-1][0] == "/terms/%s" % term.term_id
        assert (
            self.client.get("/terms?id=%s" % term.term_id, follow=True).status_code
            == 200
        )

    def test_all_terms(self):
        """Check that "all terms" page is viewable."""
        self.login()
        response = self.client.get("/terms", follow=True)
        assert response.status_code == 200

    def test_comments(self):
        """Check that comments are available."""
        self.login()
        term = Terms.objects.first()
        assert self.client.get("/terms/%s/comments" % term.term_id).status_code == 200
