from api.tests.factories import UserFactory
from api.tests.fixtures import *  # noqa: F403
from pytest_factoryboy import register

register(UserFactory)
