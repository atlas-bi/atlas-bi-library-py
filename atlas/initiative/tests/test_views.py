"""Atlas Initiative tests.

Run test for this app with::

    docker container start postgresql-container
    docker container start solr_dev

    poetry run coverage erase; \
    poetry run coverage run -p manage.py \
        test initiative/ --no-input --pattern="test_views.py" --settings atlas.settings.test; \
    poetry run coverage combine; \
    poetry run coverage report --include "initiative*" -m

"""
# pylint: disable=C0115,C0103

from index.models import Collections, Initiatives

from atlas.testutils import AtlasTestCase


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
        self.login_admin()
        initiative = Initiatives.objects.order_by("initiative_id").last()
        page = self.client.get("/initiatives/%s" % (initiative.initiative_id + 1))
        self.assertIn(b"Sorry that page could not be found.", page.content)
        self.assertIn(
            page.status_code,
            [302, 404],
        )
        # if we already hit the error page, we could potentially get a 302 response.

        # try to delete it
        page = self.client.get(
            "/initiatives/%s/delete" % (initiative.initiative_id + 1)
        )

        self.assertIn(
            page.status_code,
            [302, 404],
        )

    def test_valid_initiative(self):
        """Check that valid initiatives are viewable."""
        self.login()
        initiative = Initiatives.objects.first()
        response = self.client.get("/initiatives/%s" % initiative.initiative_id)

        self.assertEqual(response.status_code, 200)

        # self.verify_body_links(response.content)

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

        # self.verify_body_links(response.content)

    def test_get_create_initiative(self):
        """Check that an initiative can be created."""
        self.login_admin()

        response = self.client.get("/initiatives/new", follow=False)
        self.assertEqual(response.status_code, 200)

    def test_create_initiative(self):
        """Test creating, editing and deleting an initiative."""
        self.login_admin()

        data = {
            "name": "test initiative",
            "description": "initiative description",
            "ops_owner_id": "1",
            "exec_owner_id": "1",
            "financial_impact_id": "1",
            "strategic_importance_id": "1",
            "linked_data_collections": ["1"],
        }
        linked_data_collection = data["linked_data_collections"][0]

        response = self.client.post("/initiatives/new", data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        # last_url = response.redirect_chain[-1][0]
        # initiative_id = last_url[last_url.rindex("/") + 1 :]  # noqa: E203

        # # verify that the new initiative exists
        # initiative = Initiatives.objects.get(initiative_id=initiative_id)

        # # check name, summary, tech def
        # self.assertEqual(initiative.name, data["name"])
        # self.assertEqual(initiative.description, data["description"])
        # self.assertEqual(initiative.ops_owner_id, int(data["ops_owner_id"]))
        # self.assertEqual(initiative.exec_owner_id, int(data["exec_owner_id"]))
        # self.assertEqual(
        #     initiative.financial_impact_id, int(data["financial_impact_id"])
        # )
        # self.assertEqual(
        #     initiative.strategic_importance_id, int(data["strategic_importance_id"])
        # )

        # # check collection links
        # self.assertTrue(
        #     Collections.objects.filter(collection_id=linked_data_collection)
        #     .filter(initiative_id=initiative_id)
        #     .exists()
        # )

        # # change some things
        # data.pop("description")
        # data.pop("ops_owner_id")
        # data.pop("exec_owner_id")
        # data.pop("strategic_importance_id")
        # data.pop("financial_impact_id")
        # data.pop("linked_data_collections")

        # response = self.client.post(
        #     "/initiatives/%s/edit" % initiative_id, data=data, follow=True
        # )
        # self.assertEqual(response.status_code, 200)

        # # check link
        # self.assertTrue(
        #     response.redirect_chain[-1][0].endswith("/initiatives/%s" % initiative_id)
        # )

        # # refresh initiative instance
        # initiative = Initiatives.objects.get(initiative_id=initiative_id)
        # self.assertEqual(initiative.name, data["name"])
        # self.assertEqual(initiative.description, "")
        # self.assertEqual(initiative.ops_owner_id, None)
        # self.assertEqual(initiative.exec_owner_id, None)
        # self.assertEqual(initiative.financial_impact, None)
        # self.assertEqual(initiative.strategic_importance, None)

        # # check collection links
        # self.assertEqual(
        #     Collections.objects.filter(collection_id=linked_data_collection)
        #     .filter(initiative_id=initiative_id)
        #     .exists(),
        #     False,
        # )

        # # delete initiative
        # response = self.client.post(
        #     "/initiatives/%s/delete" % initiative_id, follow=True
        # )
        # self.assertEqual(response.status_code, 200)

        # self.assertTrue(response.redirect_chain[-1][0].endswith("initiatives/"))

        # # check that is was removed from db
        # self.assertEqual(
        #     Initiatives.objects.filter(initiative_id=initiative_id).exists(), False
        # )
