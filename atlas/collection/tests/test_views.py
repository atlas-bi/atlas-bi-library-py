"""Atlas Collection tests.

Run test for this app with::

    poetry run coverage erase; \
    poetry run coverage run -p manage.py \
        test collection/ --no-input --pattern="test_views.py" --settings atlas.settings.test; \
    poetry run coverage combine; \
    poetry run coverage report --include "collection*" -m

"""
import pysolr
from django.conf import settings
from etl.tasks.search.collections import load_collections
from index.models import CollectionReports, Collections, CollectionTerms

from atlas.testutils import AtlasTestCase

# pylint: disable=C0103,W0105,C0115


class CollectionTestCase(AtlasTestCase):
    # pre-login tests.
    # verify that all pages redirect to login screen.

    def test_login_collections(self):
        """Check that users are sent from ``/collections`` to login page."""
        response = self.client.get("/collections/", follow=False)
        self.assertEqual(response.url, "/accounts/login/?next=/collections/")
        self.assertEqual(response.status_code, 302)

    def test_login_collection(self):
        """Check that users are sent from ``/collections/%s`` to login page."""
        collection = Collections.objects.first()
        response = self.client.get(
            "/collections/%s" % collection.collection_id, follow=False
        )
        self.assertEqual(
            response.url,
            "/accounts/login/?next=/collections/%s" % collection.collection_id,
        )
        self.assertEqual(response.status_code, 302)

    # logged in tests.

    def test_invalid_collection(self):
        """Check that invalid collections redirect."""
        # find an collection that doesn't exist.
        self.login()

        collection = Collections.objects.order_by("collection_id").last()

        assert (
            self.client.get(
                "/collections/%s" % (collection.collection_id + 1)
            ).status_code
            == 404
        )

    def test_valid_collection(self):
        """Check that valid collections are viewable."""
        self.login()
        collection = Collections.objects.first()
        response = self.client.get("/collections/%s" % collection.collection_id)

        self.assertEqual(response.status_code, 200)

        # self.verify_body_links(response.content)

    def test_old_urls(self):
        """Check that atlas v1 urls are viewable."""
        self.login()
        collection = Collections.objects.first()
        response = self.client.get(
            "/collections?id=%s" % collection.collection_id, follow=True
        )
        assert (
            response.redirect_chain[-1][0]
            == "/collections/%s" % collection.collection_id
        )
        assert (
            self.client.get(
                "/collections?id=%s" % collection.collection_id, follow=True
            ).status_code
            == 200
        )

    def test_all_collections(self):
        """Check that "all collections" page is viewable."""
        self.login()
        response = self.client.get("/collections", follow=True)
        self.assertEqual(response.status_code, 200)

        # self.verify_body_links(response.content)

    def test_create_edit_collection(self):
        """Check that collections can be created/edited/delete."""
        self.login()

        # create new collection
        data = {
            "name": "test collection",
            "search_summary": "testing, yeah bro",
            "description": "collection description",
            "hidden": "Y",
        }

        response = self.client.post("/collections/new", data=data, follow=True)
        self.assertEqual(response.status_code, 200)

        # last_url = response.redirect_chain[-1][0]
        # collection_id = last_url[last_url.rindex("/") + 1 :]  # noqa: E203

        # # verify that the new collection exists
        # collection = Collections.objects.get(collection_id=collection_id)

        # # verify that hidden collection is not in search

        # load_collections(collection_id)
        # solr = pysolr.Solr(settings.SOLR_URL)
        # results = solr.search(q="type:collections AND atlas_id:%s" % collection_id)
        # self.assertEqual(results.hits, 0)

        # # check name, summary, tech def
        # self.assertEqual(collection.name, data["name"])
        # self.assertEqual(collection.search_summary, data["search_summary"])
        # self.assertEqual(collection.description, data["description"])
        # self.assertEqual(collection.hidden, "Y" if data["hidden"] == "Y" else "N")

        # # edit collection
        # data.pop("search_summary")
        # data.pop("hidden")

        # data["description"] = "edited description"

        # response = self.client.post(
        #     "/collections/%s/edit" % collection_id, data=data, follow=True
        # )
        # self.assertEqual(response.status_code, 200)

        # # reload collection
        # collection = Collections.objects.get(collection_id=collection_id)

        # # verify that the collection is now visible in search
        # load_collections(collection_id)
        # results = solr.search(q="type:collections AND atlas_id:%s" % collection_id)
        # self.assertEqual(results.hits, 1)

        # # check name, summary, tech def
        # self.assertEqual(collection.name, data["name"])
        # self.assertEqual(collection.search_summary, "")
        # self.assertEqual(collection.description, data["description"])
        # self.assertEqual(collection.hidden, "N")

        # # add checklist

        # # complete checklist task

        # # add attachment

        # # delete the collection
        # response = self.client.get(
        #     "/collections/%s/delete" % collection_id, follow=True
        # )
        # self.assertEqual(response.status_code, 200)

        # self.assertTrue(response.redirect_chain[-1][0].endswith("collections/"))

        # # check that is was removed from db
        # self.assertEqual(
        #     Collections.objects.filter(collection_id=collection_id).exists(), False
        # )

        # # check that collection was removed from search
        # load_collections(collection_id)
        # results = solr.search(q="type:collections AND atlas_id:%s" % collection_id)
        # self.assertEqual(results.hits, 0)
