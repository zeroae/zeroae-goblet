import pytest
from chalice import Chalice


@pytest.fixture
def app(default_config) -> Chalice:
    from zeroae.goblet.chalice import bp

    app: Chalice = Chalice(app_name="gh-app")
    app.experimental_feature_flags.update(["BLUEPRINTS"])
    app.register_blueprint(bp, name_prefix="gh")
    yield app
