import pytest
from chalice import Chalice
from environs import Env


@pytest.fixture
def env() -> Env:
    return Env()


@pytest.fixture
def default_config(env):
    from zeroae.goblet.chalice import configure

    configure(env)


@pytest.fixture
def app(default_config) -> Chalice:
    from zeroae.goblet.chalice import bp

    app: Chalice = Chalice(app_name="gh-app")
    app.experimental_feature_flags.update(["BLUEPRINTS"])
    app.register_blueprint(bp, name_prefix="gh")
    yield app
