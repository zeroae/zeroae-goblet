from collections import defaultdict
from http import HTTPStatus
from typing import DefaultDict

import pytest
from pubsub import pub
from pytest_chalice.handlers import RequestHandler

import zeroae
from zeroae.goblet.chalice import bp


@pytest.fixture
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")


@pytest.fixture
def mock_request(monkeypatch) -> DefaultDict:
    responses = defaultdict()
    monkeypatch.setattr(
        "requests.sessions.Session.request",
        lambda *a, **kw: responses[(kw["method"], kw["url"])],
    )
    return responses


@pytest.fixture(
    params=[
        {"host": "localhost"},
        {"host": "this-is-real.com", "x-forwarded-proto": "https"},
    ]
)
def mock_headers(request):
    return request.param


def test_register(client: RequestHandler, mock_headers):
    response = client.get("/", headers=mock_headers)
    assert response.status_code == HTTPStatus.OK


def test_register_callback_no_code(client: RequestHandler, mock_headers):
    response = client.get("/callback", headers=mock_headers)
    assert response.status_code == HTTPStatus.EXPECTATION_FAILED


def test_register_callback(
    client: RequestHandler, monkeypatch, mock_headers, mock_request
):
    code = "mock-code"

    class MockResponse:
        @staticmethod
        def json():
            return {"html_url": "http://next.test"}

    mock_request.default_factory = lambda *a, **kw: MockResponse()

    monkeypatch.setattr(
        zeroae.goblet.config, "save_app_registration", lambda *a, **kw: True
    )
    response = client.get(f"/callback?code={code}", headers=mock_headers)
    assert response.status_code == HTTPStatus.SEE_OTHER


def test_events(client: RequestHandler, monkeypatch, mock_headers, no_requests):
    monkeypatch.setattr("pubsub.pub.sendMessage", lambda *args, **kwargs: True)
    mock_headers["x-github-event"] = "mock"

    monkeypatch.setattr("octokit.webhook.verify", lambda *args, **kwargs: True)
    # 📜: There is a bug in chalice that erases route method information...
    response = client.get(f"/events", headers=mock_headers, body="{}")
    assert response.status_code == HTTPStatus.OK

    monkeypatch.setattr("octokit.webhook.verify", lambda *args, **kwargs: False)
    response = client.get(f"/events", headers=mock_headers, body="{}")
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_on_gh_event():
    @bp.on_gh_event("mock")
    def ping(payload):
        pass

    assert pub.getDefaultTopicMgr().getTopic("gh.mock") is not None
