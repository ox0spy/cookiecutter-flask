import pytest

from {{cookiecutter.app_name}}.config import conf
from {{cookiecutter.app_name}}.main import app_factory


@pytest.fixture
def app():
    return app_factory(conf)
