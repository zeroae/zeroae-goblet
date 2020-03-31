import pytest
from environs import Env


@pytest.fixture
def env() -> Env:
    return Env()


@pytest.fixture
def default_config(env):
    from zeroae.goblet.chalice import configure

    configure(env)
