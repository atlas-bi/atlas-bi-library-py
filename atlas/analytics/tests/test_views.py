"""Atlas Analytics tests.

run with::

    poetry run coverage erase; \
    poetry run coverage run -p manage.py \
        test analytics/ --no-input --pattern="test_views.py" --settings atlas.settings.test; \
    poetry run coverage combine; \
    poetry run coverage report --include "analytics*" -m

"""
# pylint: disable=C0115,C0103,C0301

import json

from atlas.testutils import AtlasTestCase


class AnalyticsTestCase(AtlasTestCase):
    def test_index_user(self):
        """Basic users should be not authorized.

        Expecting a 302 redirect back to login page.
        """
        self.login()
        response = self.client.get("/analytics/")
        self.assertEqual(response.status_code, 302)

    def test_index_admin(self):
        """Admin should have access."""
        self.login_admin()
        response = self.client.get("/analytics/")
        self.assertEqual(response.status_code, 200)

        # self.verify_body_links(response.content)

    def test_log(self):
        """Test analytics logging."""
        self.login()
        data = {
            "language": "en-us",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",  # noqa: E501
            "hostname": "127.0.0.1",
            "href": "http: //127.0.0.1:8000/analytics/",
            "protocol": "http: ",
            "search": "",
            "pathname": "/analytics/",
            "screenHeight": 1335,
            "screenWidth": 1998,
            "origin": "http: //127.0.0.1:8000",
            "title": "Analytics - Atlas",
            "referrer": "",
            "loadTime": 9135,
            "zoom": 1,
            "sessionId": "V2VkIEFwciAyOCAyMDIxIDEwOjIzOjEwIEdNVC0wNTAwIChDRFQp",
            "pageId": "V2VkIEFwciAyOCAyMDIxIDEwOjIzOjEwIEdNVC0wNTAwIChDRFQp",
            "pageTime": 46,
        }

        response = self.client.post(
            "/analytics/log", data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)

        # send a 2nd time to check "exists" code.
        response = self.client.post(
            "/analytics/log", data=json.dumps(data), content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
