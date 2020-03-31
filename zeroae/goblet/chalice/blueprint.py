#  Copyright (c) 2020 Zero A.E., LLC
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
from http import HTTPStatus
from urllib.parse import urljoin

from chalice import Blueprint, Response
from chalice.app import Request, ForbiddenError
from octokit import webhook
from pubsub import pub
from pubsub.utils import ExcPublisher

from zeroae.goblet.utils import (
    create_app_manifest,
    infer_app_url,
    get_create_app_url,
    get_configured_octokit,
)
from .. import config
from ..views import render_setup_html


class GitHubAppBlueprint(Blueprint):
    def __init__(self, import_name):
        """Creates the Chalice GitHubApp Blueprint."""
        super().__init__(import_name)
        pub.setListenerExcHandler(ExcPublisher(pub.getDefaultTopicMgr()))

    @staticmethod
    def on_gh_event(topic):
        """
        :param topic: The GitHub webhook topic
        :return: decorator
        """

        def decorator(f):
            l, _ = pub.subscribe(f, "gh" if topic == "*" else f"gh.{topic}")
            f.listener = l
            return f

        return decorator


bp: GitHubAppBlueprint = GitHubAppBlueprint(__name__)


@bp.route("/")
def register():
    """
    Note: HTTP Post Redirect, 307 code
    ref: bit.ly/why-doesnt-http-have-post-redirect
    :return:
    """
    # Get GitHub's create_app_url, for user/owner application
    create_app_url = get_create_app_url()

    request: Request = bp.current_request
    app_url = infer_app_url(request.headers, request.context["path"])
    app_manifest = create_app_manifest(app_url)
    body = render_setup_html(app_manifest, create_app_url)
    return Response(
        body=body, status_code=HTTPStatus.OK, headers={"Content-Type": "text/html"}
    )


@bp.route("/callback")
def register_callback():
    """
    Finishes the GitHub Application Registration flow.
    1. Converts code for clientId, clientSecret, webhook secret, and App PEM
    2. Saves result in the configuration backend
    :return:
    """
    query_params = bp.current_request.query_params
    query_params = query_params if query_params else dict()

    code = query_params.get("code", None)
    if code is None:
        return Response(
            body='{"error": "The GitHub application-manifest code is missing."}',
            status_code=HTTPStatus.EXPECTATION_FAILED,
            headers={"Content-Type": "text/html"},
        )

    o = get_configured_octokit()
    o = o.apps.create_from_manifest(code=code)

    config.save_app_registration(o.json)

    return Response(
        body="",
        status_code=HTTPStatus.SEE_OTHER,
        headers={"Location": urljoin(f'{o.json["html_url"]}/', "installations/new")},
    )


@bp.route("/events", methods=["POST"])
def events():
    if not webhook.verify(
        bp.current_request.headers,
        bp.current_request.raw_body.decode("utf-8"),
        config.APP_WEBHOOK_SECRET,
        events=["*"],
    ):
        raise ForbiddenError(
            f"Error validating the event: {bp.current_request.to_dict()}"
        )

    r: Request = bp.current_request
    event_topic = r.headers["x-github-event"]
    pub.sendMessage(f"gh.{event_topic}", payload=r.json_body)
    return {}
