"""Atlas Project tests.

Run test for this app with::

    poetry run coverage erase; \
    poetry run coverage run -p manage.py \
        test project/ --no-input --pattern="test_views.py" --settings atlas.settings.test; \
    poetry run coverage combine; \
    poetry run coverage report --include "project*" -m

"""
import pysolr
from django.conf import settings
from etl.tasks.search.projects import load_projects
from index.models import (
    ProjectComments,
    ProjectCommentStream,
    ProjectReports,
    Projects,
    ProjectTerms,
)

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
            "hidden": "Y",
        }

        response = self.client.post("/projects/new", data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        last_url = response.redirect_chain[-1][0]
        project_id = last_url[last_url.rindex("/") + 1 :]  # noqa: E203

        # verify that the new project exists
        project = Projects.objects.get(project_id=project_id)

        # verify that hidden project is not in search

        load_projects(project_id)
        solr = pysolr.Solr(settings.SOLR_URL)
        results = solr.search(q="type:projects AND atlas_id:%s" % project_id)
        self.assertEqual(results.hits, 0)

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
        self.assertEqual(project.hidden, "Y" if data["hidden"] == "Y" else "N")

        # edit project
        data.pop("purpose")
        data.pop("hidden")

        data.pop("ops_owner_id")
        data.pop("exec_owner_id")
        data.pop("analytics_owner_id")
        data.pop("data_owner_id")
        data.pop("external_documentation_url")

        data["financial_impact_id"] = "2"
        data["strategic_importance_id"] = "2"

        data["description"] = "edited description"

        response = self.client.post(
            "/projects/%s/edit" % project_id, data=data, follow=True
        )
        self.assertEqual(response.status_code, 200)

        # reload project
        project = Projects.objects.get(project_id=project_id)

        # verify that the project is now visible in search
        load_projects(project_id)
        results = solr.search(q="type:projects AND atlas_id:%s" % project_id)
        self.assertEqual(results.hits, 1)

        # check name, summary, tech def
        self.assertEqual(project.name, data["name"])
        self.assertEqual(project.purpose, "")
        self.assertEqual(project.description, data["description"])
        self.assertEqual(project.ops_owner_id, None)
        self.assertEqual(project.exec_owner_id, None)
        self.assertEqual(project.analytics_owner_id, None)
        self.assertEqual(project.data_owner_id, None)
        self.assertEqual(project.financial_impact_id, int(data["financial_impact_id"]))
        self.assertEqual(
            project.strategic_importance_id, int(data["strategic_importance_id"])
        )
        self.assertEqual(project.external_documentation_url, "")
        self.assertEqual(project.hidden, "N")

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

        # check that project was removed from search
        load_projects(project_id)
        results = solr.search(q="type:projects AND atlas_id:%s" % project_id)
        self.assertEqual(results.hits, 0)

    def test_create_comments(self):
        """Check that we can create comments."""
        self.login()
        project = Projects.objects.first()
        data = {"message": "new comment"}
        self.assertEqual(
            self.client.post(
                "/projects/%s/comments" % project.project_id,
                data=data,
                content_type="application/json",
            ).status_code,
            302,
        )

        # assert that the comment stream was created
        self.assertTrue(
            ProjectCommentStream.objects.filter(project_id=project.project_id)
            .filter(comments__message=data["message"])
            .exists()
        )

        # assert that the comment was created
        self.assertTrue(
            ProjectComments.objects.filter(stream__project_id=project.project_id)
            .filter(message=data["message"])
            .exists()
        )

        # attempt to add a second stream and verify it
        data = {"message": "new comment two"}
        self.assertEqual(
            self.client.post(
                "/projects/%s/comments" % project.project_id,
                data=data,
                content_type="application/json",
            ).status_code,
            302,
        )
        self.assertTrue(
            ProjectComments.objects.filter(stream__project_id=project.project_id)
            .filter(message=data["message"])
            .exists()
        )
        self.assertTrue(
            ProjectCommentStream.objects.filter(project_id=project.project_id)
            .filter(comments__message=data["message"])
            .exists()
        )

        # attempt to add another comment to the streamand verify it is there
        stream = (
            ProjectComments.objects.filter(stream__project_id=project.project_id)
            .filter(message=data["message"])
            .first()
        )
        data = {"message": "stream reply", "stream": stream.stream_id}
        self.assertEqual(
            self.client.post(
                "/projects/%s/comments" % project.project_id,
                data=data,
                content_type="application/json",
            ).status_code,
            302,
        )
        self.assertTrue(
            ProjectComments.objects.filter(stream__project_id=project.project_id)
            .filter(message=data["message"])
            .filter(stream_id=stream.stream_id)
            .exists()
        )
        self.assertTrue(
            ProjectCommentStream.objects.filter(project_id=project.project_id)
            .filter(comments__message=data["message"])
            .filter(stream_id=stream.stream_id)
            .exists()
        )

        # attempt to delete a comment and verify it is gone
        comment = ProjectComments.objects.filter(
            stream__project_id=project.project_id
        ).first()
        self.assertTrue(
            self.client.post(
                "/projects/%s/comments/%s/delete"
                % (
                    project.project_id,
                    comment.comment_id,
                ),
                content_type="application/json",
            ),
            302,
        )

        # attempt to delete a stream
        comment = ProjectComments.objects.filter(
            stream__project_id=project.project_id
        ).first()
        data = {"stream": comment.stream_id}
        self.assertTrue(
            self.client.post(
                "/projects/%s/comments/%s/delete"
                % (
                    project.project_id,
                    comment.comment_id,
                ),
                data=data,
                content_type="application/json",
            ),
            302,
        )

        # add a comment with no message
        self.assertEqual(
            self.client.post(
                "/projects/%s/comments" % project.project_id,
                content_type="application/json",
            ).status_code,
            302,
        )

    def test_add_report_annotation(self):
        """Test adding and removing a report annotation."""
        self.login()
        data = {
            "annotation": "# this is \n\n ## amazing",
            "rank": "9",
            "report_id": "1",
        }

        # check with wrong method
        response = self.client.get(
            "/projects/1/edit/reports",
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

        # check with invalid report id
        data["report_id"] = 99
        response = self.client.post(
            "/projects/1/edit/reports",
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # check wtih valid data
        data["report_id"] = 1

        response = self.client.post(
            "/projects/1/edit/reports",
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            ProjectReports.objects.filter(annotation=data["annotation"])
            .filter(rank=data["rank"])
            .filter(project_id=1)
            .exists()
        )

        annotation_id = (
            ProjectReports.objects.filter(annotation=data["annotation"])
            .filter(rank=data["rank"])
            .filter(project_id=1)
            .first()
            .annotation_id
        )

        # edit the annotation
        data.pop("rank")
        data["annotation"] = "new annotation"

        response = self.client.post(
            "/projects/1/edit/reports/%s" % annotation_id,
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            ProjectReports.objects.filter(annotation=data["annotation"])
            .filter(rank=None)
            .filter(project_id=1)
            .exists()
        )

        # delete the annotation
        response = self.client.get("/projects/1/edit/reports/%s/delete" % annotation_id)
        self.assertEqual(response.status_code, 200)

        # make sure its gone
        self.assertEqual(
            ProjectReports.objects.filter(annotation_id=annotation_id).exists(), False
        )

    def test_add_term_annotation(self):
        """Test adding and removing a term annotation."""
        self.login()
        data = {"annotation": "# this is \n\n ## amazing", "rank": "9", "term_id": "1"}

        # check with wrong method
        response = self.client.get(
            "/projects/1/edit/terms",
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

        # check with invalid term id
        data["term_id"] = 99
        response = self.client.post(
            "/projects/1/edit/terms",
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # check wtih valid data
        data["term_id"] = 1

        response = self.client.post(
            "/projects/1/edit/terms",
            data=data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            ProjectTerms.objects.filter(annotation=data["annotation"])
            .filter(rank=data["rank"])
            .filter(project_id=1)
            .exists()
        )

        annotation_id = (
            ProjectTerms.objects.filter(annotation=data["annotation"])
            .filter(rank=data["rank"])
            .filter(project_id=1)
            .first()
            .annotation_id
        )

        # edit the annotation
        data.pop("rank")
        data["annotation"] = "new annotation"

        response = self.client.post(
            "/projects/1/edit/terms/%s" % annotation_id,
            data=data,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.assertTrue(
            ProjectTerms.objects.filter(annotation=data["annotation"])
            .filter(rank=None)
            .filter(project_id=1)
            .exists()
        )

        # delete the annotation
        response = self.client.get("/projects/1/edit/terms/%s/delete" % annotation_id)
        self.assertEqual(response.status_code, 200)

        # make sure its gone
        self.assertEqual(
            ProjectTerms.objects.filter(annotation_id=annotation_id).exists(), False
        )
