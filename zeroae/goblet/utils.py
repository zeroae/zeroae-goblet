from typing import Dict, Any
from urllib.parse import urljoin

import octokit

from zeroae.goblet import config


def get_configured_octokit(*args, **kwargs) -> octokit.Octokit:
    kwargs["specification"] = config.GHE_API_SPEC
    rv = octokit.Octokit(*args, **kwargs)
    rv.base_url = config.GHE_API_URL.geturl()
    return rv


def create_app_manifest(app_url: str) -> Dict[str, Any]:
    """
    Returns the GitHub Application Manifest based on the chalice application settings.

    ref: https://bit.ly/creating-github-apps-from-a-manifest
    :param app_url:
    :param current_request:
    :return: The GitHub Application Manifest
    """
    webhook_proxy_url = config.WEBHOOK_PROXY_URL.geturl()
    hook_url: str = (
        urljoin(app_url, "events") if webhook_proxy_url == b"" else webhook_proxy_url
    )

    return dict(
        name=config.APP_NAME,
        description=config.APP_DESCRIPTION,
        url=app_url,
        redirect_url=urljoin(app_url, "callback"),
        hook_attributes=dict(url=hook_url),
        public=config.APP_PUBLIC,
        default_permissions=config.APP_DEFAULT_PERMISSIONS,
        default_events=config.APP_DEFAULT_EVENTS,
    )


def infer_app_url(headers: dict, register_path: str) -> str:
    """
    ref: github.com/aws/chalice#485
    :return: The Chalice Application URL
    """
    host: str = headers["host"]
    scheme: str = headers.get("x-forwarded-proto", "http")
    app_url: str = f"{scheme}://{host}{register_path}"
    return app_url


def get_create_app_url():
    """
    Returns GitHub's Create Application URL
    :return:
    """
    org = config.APP_ORGANIZATION
    org_path = f"/organizations/{org}" if org else ""

    proto = config.GHE_PROTO
    host = config.GHE_HOST

    return f"{proto}://{host}{org_path}/settings/apps/new"
