import pytest
from flask import testing

from main import create_app


@pytest.fixture()
def app():
    test_config = {
        "DEBUG": True,  # some Flask specific configs
        # "CACHE_TYPE": "FileSystemCache",
        # "CACHE_DIR": "cache",  # Flask-Caching related configs
        # "CACHE_DEFAULT_TIMEOUT": 300
    }
    app = create_app()
    app.config.update({
        "TESTING": True,
        "JSON_SORT_KEYS": False,
    })
    yield app


class TestClient(testing.FlaskClient):
    def open(self, *args, **kwargs):
        return super().open(*args, **kwargs)


@pytest.fixture()
def client(app):
    app.test_client_class = TestClient
    return app.test_client()
