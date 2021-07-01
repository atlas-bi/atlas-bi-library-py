"""Test runner for browser stack tests.

A custom test runner is used so that we can run the tests
with multiple browser configurations.
"""
# pylint: disable=C0115
from browserstack.local import Local
from django.conf import settings
from django.test.runner import DiscoverRunner


class BrowserStackDiscoverRunner(DiscoverRunner):
    """Custom runner for browserstack.

    This runner allows us to run tests for multiple browser configurations.
    """

    def run_suite(self, suite, **kwargs):
        """Override run_suite with a for loop function."""
        suite._cleanup = False
        bs_local = Local()
        bs_local_args = {"forcelocal": "true"}
        bs_local.start(**bs_local_args)

        print(
            "Browser stack is %srunning..." % ("" if bs_local.isRunning() else "not ")
        )  # noqa: T001

        result = {}
        for cap in getattr(settings, "BROWSERSTACK_CAPS", {}):
            settings.WEBDRIVER = cap
            kwargs = self.get_test_runner_kwargs()
            runner = self.test_runner(**kwargs)
            result = runner.run(suite)

        # return last result.. not sure how to merge them
        bs_local.stop()

        return result
