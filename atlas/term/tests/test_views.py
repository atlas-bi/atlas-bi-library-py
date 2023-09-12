"""Term app tests.

Run test for this app with::

    poetry run coverage erase; \
    poetry run coverage run -p manage.py \
        test term/ --no-input --pattern="test_views.py" --settings atlas.settings.test; \
    poetry run coverage combine; \
    poetry run coverage report --include "term*" -m

"""
from django.utils import timezone
from index.models import (
    Collections,
    CollectionTerms,
    ReportDocs,
    ReportTerms,
    TermComments,
    TermCommentStream,
    Terms,
)

from atlas.testutils import AtlasTestCase

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

        # try to get it
        self.assertEqual(
            self.client.get("/terms/%s" % (term.term_id + 1)).status_code, 404
        )

        # try to delete it
        self.assertEqual(
            self.client.get("/terms/%s/delete" % (term.term_id + 1)).status_code, 404
        )

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

        self.verify_body_links(response.content)

    def test_comments(self):
        """Check that comments are available."""
        self.login()
        term = Terms.objects.first()
        assert self.client.get("/terms/%s/comments" % term.term_id).status_code == 200

    def test_create_comments(self):
        """Check that we can create comments."""
        self.login()
        term = Terms.objects.first()
        data = {"message": "new comment"}
        self.assertEqual(
            self.client.post(
                "/terms/%s/comments" % term.term_id,
                data=data,
                content_type="application/json",
            ).status_code,
            200,
        )

        # assert that the comment stream was created
        self.assertTrue(
            TermCommentStream.objects.filter(term_id=term.term_id)
            .filter(comments__message=data["message"])
            .exists()
        )

        # assert that the comment was created
        self.assertTrue(
            TermComments.objects.filter(stream__term_id=term.term_id)
            .filter(message=data["message"])
            .exists()
        )

        # attempt to add a second stream and verify it
        data = {"message": "new comment two"}
        self.assertEqual(
            self.client.post(
                "/terms/%s/comments" % term.term_id,
                data=data,
                content_type="application/json",
            ).status_code,
            200,
        )
        self.assertTrue(
            TermComments.objects.filter(stream__term_id=term.term_id)
            .filter(message=data["message"])
            .exists()
        )
        self.assertTrue(
            TermCommentStream.objects.filter(term_id=term.term_id)
            .filter(comments__message=data["message"])
            .exists()
        )

        # attempt to add another comment to the streamand verify it is there
        stream = (
            TermComments.objects.filter(stream__term_id=term.term_id)
            .filter(message=data["message"])
            .first()
        )
        data = {"message": "stream reply", "stream": stream.stream_id}
        self.assertEqual(
            self.client.post(
                "/terms/%s/comments" % term.term_id,
                data=data,
                content_type="application/json",
            ).status_code,
            200,
        )
        self.assertTrue(
            TermComments.objects.filter(stream__term_id=term.term_id)
            .filter(message=data["message"])
            .filter(stream_id=stream.stream_id)
            .exists()
        )
        self.assertTrue(
            TermCommentStream.objects.filter(term_id=term.term_id)
            .filter(comments__message=data["message"])
            .filter(stream_id=stream.stream_id)
            .exists()
        )

        # attempt to delete a comment and verify it is gone
        comment = TermComments.objects.filter(stream__term_id=term.term_id).first()
        self.assertTrue(
            self.client.post(
                "/terms/%s/comments/%s/delete"
                % (
                    term.term_id,
                    comment.comment_id,
                ),
                content_type="application/json",
            ),
            302,
        )

        # attempt to delete a stream
        comment = TermComments.objects.filter(stream__term_id=term.term_id).first()
        data = {"stream": comment.stream_id}
        self.assertTrue(
            self.client.post(
                "/terms/%s/comments/%s/delete"
                % (
                    term.term_id,
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
                "/terms/%s/comments" % term.term_id, content_type="application/json"
            ).status_code,
            200,
        )

    def test_create_term(self):
        """Check that we can create and edit terms."""
        self.login()

        # first with all details
        data = {
            "name": "test term",
            "summary": "term summary",
            "technical_definition": "term deff",
        }
        response = self.client.post("/terms/new", data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        last_url = response.redirect_chain[-1][0]
        term_id = last_url[last_url.rindex("/") + 1 :]  # noqa: E203

        # verify that the new term exists
        term = Terms.objects.get(term_id=term_id)

        # check it is not approved
        self.assertEqual(term.approved, "N")
        self.assertEqual(term._approved_at, None)

        # approve the term
        data["approved"] = "Y"

        response = self.client.post("/terms/%s/edit" % term_id, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        # refresh term instance
        term = Terms.objects.get(term_id=term_id)

        # verify that it is approved
        self.assertEqual(term.approved, "Y")
        self.assertTrue(term._approved_at is not None)

        # create a term approved
        data["approved"] = "Y"
        response = self.client.post("/terms/new", data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        last_url = response.redirect_chain[-1][0]
        term_id = last_url[last_url.rindex("/") + 1 :]  # noqa: E203

        # verify that the new term exists
        term = Terms.objects.get(term_id=term_id)

        # check name, summary, tech def
        self.assertEqual(term.name, data["name"])
        self.assertEqual(term.summary, data["summary"])
        self.assertEqual(term.technical_definition, data["technical_definition"])

        # verify there is no documentation
        self.assertEqual(term.external_standard_url, "")

        # check that get sends us back to the term.
        self.assertEqual(self.client.get("/terms/new").status_code, 302)

        # unapprove the term
        data["approved"] = "N"
        response = self.client.post("/terms/%s/edit" % term_id, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        # refresh term instance
        term = Terms.objects.get(term_id=term_id)

        # verify that it is not approved
        self.assertEqual(term.approved, "N")
        self.assertEqual(term._approved_at, None)

        # add external documentation
        data["external_standard_url"] = "out://er.space"
        response = self.client.post("/terms/%s/edit" % term_id, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        # refresh term instance
        term = Terms.objects.get(term_id=term_id)

        # verify it is there
        self.assertEqual(term.external_standard_url, data["external_standard_url"])

        # remove external documentation
        data.pop("external_standard_url")
        response = self.client.post("/terms/%s/edit" % term_id, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        # refresh term instance
        term = Terms.objects.get(term_id=term_id)

        # verify that it is gone
        self.assertEqual(term.external_standard_url, "")

        # check valid from
        data["valid_from"] = timezone.now()
        response = self.client.post("/terms/%s/edit" % term_id, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        # refresh term instance
        term = Terms.objects.get(term_id=term_id)

        # check date
        self.assertEqual(term._valid_from, data["valid_from"])

        data.pop("valid_from")
        response = self.client.post("/terms/%s/edit" % term_id, data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        # refresh term instance
        term = Terms.objects.get(term_id=term_id)

        # verify that it is gone
        self.assertEqual(term._valid_from, None)

    def test_delete_term(self):
        """Try to delete a term."""
        self.login()

        # first with all details
        data = {
            "name": "test term",
            "summary": "term summary",
            "technical_definition": "term deff",
        }
        response = self.client.post("/terms/new", data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        last_url = response.redirect_chain[-1][0]
        term_id = last_url[last_url.rindex("/") + 1 :]  # noqa: E203

        # add a comment
        data = {"message": "new comment"}
        self.assertEqual(
            self.client.post(
                "/terms/%s/comments" % term_id,
                data=data,
                content_type="application/json",
            ).status_code,
            200,
        )

        # add a report link
        report_doc = ReportDocs.objects.first()
        ReportTerms(report_doc=report_doc, term_id=term_id).save()

        # verify it exists
        self.assertEqual(
            ReportTerms.objects.filter(report_doc=report_doc)
            .filter(term_id=term_id)
            .exists(),
            True,
        )

        # add a collection link
        collection = Collections.objects.first()

        CollectionTerms(collection=collection, term_id=term_id).save()

        # verify it exists
        self.assertEqual(
            CollectionTerms.objects.filter(collection=collection)
            .filter(term_id=term_id)
            .exists(),
            True,
        )

        # delete the term
        response = self.client.get("/terms/%s/delete" % term_id, follow=True)
        self.assertEqual(response.status_code, 200)

        # verify that report link is gone
        self.assertEqual(
            ReportTerms.objects.filter(report_doc=report_doc)
            .filter(term_id=term_id)
            .exists(),
            False,
        )

        # verify that the collection link is gone
        self.assertEqual(
            CollectionTerms.objects.filter(collection=collection)
            .filter(term_id=term_id)
            .exists(),
            False,
        )
