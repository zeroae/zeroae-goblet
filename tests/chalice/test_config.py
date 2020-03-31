import os
from collections import defaultdict

import pytest


@pytest.fixture
def mock_ghe_2_16_api_spec(monkeypatch):
    monkeypatch.setenv("GHE_API_SPEC", "ghe-2.16")
    monkeypatch.setenv("GHE_PROTO", "http")
    monkeypatch.setenv("GHE_HOST", "github.test")


def test_github_spec(default_config):
    from zeroae.goblet import config

    assert config.GHE_PROTO == "https"
    assert config.GHE_HOST == "github.com"
    assert config.GHE_API_SPEC == "api.github.com"
    assert config.GHE_API_URL.geturl() == "https://api.github.com"


def test_ghe_2_16_spec(env, mock_ghe_2_16_api_spec, default_config):
    from zeroae.goblet import config

    assert config.GHE_PROTO == "http"
    assert config.GHE_HOST == "github.test"
    assert config.GHE_API_SPEC == "ghe-2.16"
    assert config.GHE_API_URL.geturl() == "http://github.test/api/v3"


def test_save_app_registration(tmpdir, monkeypatch):
    from zeroae.goblet import config

    monkeypatch.chdir(tmpdir)

    config.save_app_registration(defaultdict(lambda: "mocked"))
    assert os.path.exists(".env")
    assert config.APP_ID == "mocked"
