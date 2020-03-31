import pytest


@pytest.fixture
def mock_webhook_url(monkeypatch):
    webhook_proxy_url = "https://webhookproxy.test"
    monkeypatch.setenv("WEBHOOK_PROXY_URL", webhook_proxy_url)
    yield webhook_proxy_url


def test_create_app_manifest_schema(default_config):
    from zeroae.goblet.utils import create_app_manifest

    app_url = "https://abc.test/"

    manifest = create_app_manifest(app_url)

    for str_attr in ["name", "url", "redirect_url", "description"]:
        assert str_attr in manifest
        assert isinstance(manifest[str_attr], str)

    assert "public" in manifest
    assert isinstance(manifest["public"], bool)

    # Hook Attribute Schema
    assert "hook_attributes" in manifest
    hook_attributes = manifest["hook_attributes"]
    assert isinstance(hook_attributes, dict)
    assert "url" in hook_attributes
    assert isinstance(hook_attributes["url"], str)

    # Events
    assert "default_events" in manifest
    assert isinstance(manifest["default_events"], list)

    # Permissions
    assert "default_permissions" in manifest
    default_permissions = manifest["default_permissions"]
    assert isinstance(default_permissions, dict)


def test_create_app_manifest_webhook_proxy(mock_webhook_url, default_config):
    from zeroae.goblet.utils import create_app_manifest

    app_url = "https://abc.test/"
    manifest = create_app_manifest(app_url)

    assert manifest["hook_attributes"]["url"] == mock_webhook_url


@pytest.mark.parametrize(
    "proto,register_path,expected",
    [(None, "/", "http://abc.test/"), ("https", "/", "https://abc.test/")],
)
def test_infer_app_url(proto, register_path, expected):
    from zeroae.goblet.utils import infer_app_url

    headers = {"host": "abc.test"}
    if proto:
        headers["x-forwarded-proto"] = proto

    app_url = infer_app_url(headers, register_path)
    assert app_url == expected


@pytest.fixture(params=[None, "test_org"])
def mock_app_organization(monkeypatch, request):
    if request.param is not None:
        monkeypatch.setenv("APP_ORGANIZATION", request.param)
    yield request.param


def test_get_create_app_url(mock_app_organization, default_config):
    from zeroae.goblet.utils import get_create_app_url

    app_url = get_create_app_url()

    if mock_app_organization:
        assert f"organizations/{mock_app_organization}" in app_url
    else:
        assert "organization" not in app_url
    assert app_url.endswith("settings/apps/new")
