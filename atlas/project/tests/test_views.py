"""Atlas Project tests.

Run test for this app with::

    poetry run coverage erase; \
    poetry run coverage run -p manage.py \
        test project/ --no-input --pattern="test_views.py" --settings atlas.settings.test; \
    poetry run coverage combine; \
    poetry run coverage report --include "project*" -m

"""
from index.models import Projects

from atlas.testutils import AtlasTestCase

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

    def test_create_edit_project(self):
        """Check that projects can be created/edited/delete."""
        self.login()

        # test wrong method
        response = self.client.get("/projects/new", follow=True)
        self.assertEqual(response.status_code, 200)

        # check link
        self.assertTrue(response.redirect_chain[-1][0].endswith("projects/"))

        # create new project
        data = {
            "name": "test project",
            "purpose": "testing, yeah bro",
            "description": "project description",
            "ops_owner_id": "1",
            "exec_owner_id": "1",
            "analytics_owner_id": "1",
            "data_owner_id": "1",
            "financial_impact_id": "1",
            "strategic_importance_id": "1",
            "external_documentation_url": "some://thing.cool",
            "hidden": "Yep",
        }

        response = self.client.post("/projects/new", data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        last_url = response.redirect_chain[-1][0]
        project_id = last_url[last_url.rindex("/") + 1 :]  # noqa: E203

        # verify that the new project exists
        project = Projects.objects.get(project_id=project_id)

        # check name, summary, tech def
        self.assertEqual(project.name, data["name"])
        self.assertEqual(project.purpose, data["purpose"])
        self.assertEqual(project.description, data["description"])
        self.assertEqual(project.ops_owner_id, int(data["ops_owner_id"]))
        self.assertEqual(project.exec_owner_id, int(data["exec_owner_id"]))
        self.assertEqual(project.analytics_owner_id, int(data["analytics_owner_id"]))
        self.assertEqual(project.data_owner_id, int(data["data_owner_id"]))
        self.assertEqual(project.financial_impact_id, int(data["financial_impact_id"]))
        self.assertEqual(
            project.strategic_importance_id, int(data["strategic_importance_id"])
        )
        self.assertEqual(
            project.external_documentation_url, data["external_documentation_url"]
        )
        self.assertEqual(project.hidden, "Y" if bool(data["hidden"]) else "N")

        # add term and report annotation

        # add checklist

        # complete checklist task

        # add attachment

        # delete the project
        response = self.client.get("/projects/%s/delete" % project_id, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertTrue(response.redirect_chain[-1][0].endswith("projects/"))

        # check that is was removed from db
        self.assertEqual(Projects.objects.filter(project_id=project_id).exists(), False)
