"""Atlas Project tests."""
from atlas.testutils import AtlasTestCase
from index.models import Projects

# pylint: disable=C0103,W0105,C0115


class ProjectTestCase(AtlasTestCase):

    # pre-login tests.
    # verify that all pages redirect to login screen.

    def test_login_projects(self):
        """Check that users are sent from ``/projects`` to login page."""
        response = self.client.get("/projects/", follow=False)
        self.assertEqual(response.url, "/accounts/login/?next=/projects/")
        self.assertEqual(response.status_code, 302)

    def test_login_project(self):
        """Check that users are sent from ``/projects/%s`` to login page."""
        project = Projects.objects.first()
        response = self.client.get("/projects/%s" % project.project_id, follow=False)
        self.assertEqual(
            response.url, "/accounts/login/?next=/projects/%s" % project.project_id
        )
        self.assertEqual(response.status_code, 302)

    def test_login_comments(self):
        """Check that users are sent from ``/projects/%s/comments`` to login page."""
        project = Projects.objects.first()
        response = self.client.get(
            "/projects/%s/comments" % project.project_id, follow=False
        )
        self.assertEqual(
            response.url,
            "/accounts/login/?next=/projects/%s/comments" % project.project_id,
        )
        self.assertEqual(response.status_code, 302)

    # logged in tests.

    def test_invalid_project(self):
        """Check that invalid projects redirect."""
        # find an project that doesn't exist.
        self.login()

        project = Projects.objects.order_by("project_id").last()

        assert (
            self.client.get("/projects/%s" % (project.project_id + 1)).status_code
            == 302
        )

    def test_valid_project(self):
        """Check that valid projects are viewable."""
        self.login()
        project = Projects.objects.first()
        response = self.client.get("/projects/%s" % project.project_id)

        self.assertEqual(response.status_code, 200)

        self.verify_body_links(response.content)

    def test_old_urls(self):
        """Check that atlas v1 urls are viewable."""
        self.login()
        project = Projects.objects.first()
        response = self.client.get("/projects?id=%s" % project.project_id, follow=True)
        assert response.redirect_chain[-1][0] == "/projects/%s" % project.project_id
        assert (
            self.client.get(
                "/projects?id=%s" % project.project_id, follow=True
            ).status_code
            == 200
        )

    def test_all_projects(self):
        """Check that "all projects" page is viewable."""
        self.login()
        response = self.client.get("/projects", follow=True)
        self.assertEqual(response.status_code, 200)

        self.verify_body_links(response.content)

    def test_comments(self):
        """Check that comments are available."""
        self.login()
        project = Projects.objects.first()
        assert (
            self.client.get("/projects/%s/comments" % project.project_id).status_code
            == 200
        )
