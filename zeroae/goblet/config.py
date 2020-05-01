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
import os
from typing import Dict
from urllib.parse import urlparse

from dotenv import set_key
from environs import Env
from marshmallow.validate import OneOf, ContainsOnly
from octokit_routes import specifications

# GitHub API Config
GHE_HOST = None
GHE_PROTO = None
GHE_API_URL = None
GHE_API_SPEC = None

# GitHub Application Manifest Config
APP_NAME = None
APP_DESCRIPTION = None
APP_ORGANIZATION = None
APP_PUBLIC = None
APP_DEFAULT_EVENTS = None
APP_DEFAULT_PERMISSIONS = None

# GitHub Application Registration Config
APP_ID = None
APP_CLIENT_ID = None
APP_CLIENT_SECRET = None
APP_PEM = None
APP_WEBHOOK_SECRET = None

# Other Options
WEBHOOK_PROXY_URL = None


def configure(env: Env):
    _load_ghe_options(env)
    _load_app_options(env)
    _load_app_registration_options(env)
    _load_other_options(env)


def _load_other_options(env: Env):
    global WEBHOOK_PROXY_URL
    WEBHOOK_PROXY_URL = env.url("WEBHOOK_PROXY_URL", None)


def _load_ghe_options(env: Env):
    global GHE_HOST, GHE_PROTO, GHE_API_URL, GHE_API_SPEC
    with env.prefixed("GHE_"):
        GHE_API_SPEC = env.str(
            "API_SPEC",
            "api.github.com",
            validate=OneOf(
                specifications.keys(), error="GHE_API_SPEC must be one of: {choices}"
            ),
        )
        if GHE_API_SPEC == "api.github.com":
            GHE_PROTO = "https"
            GHE_HOST = "github.com"
            GHE_API_URL = urlparse("https://api.github.com")
        else:
            GHE_PROTO = env.str(
                "PROTO",
                "https",
                validate=OneOf(
                    ["http", "https"], error="GHE_PROTO must be one of: {choices}"
                ),
            )
            GHE_HOST = env.str("HOST")
            GHE_API_URL = env.url("GHE_API_URL", f"{GHE_PROTO}://{GHE_HOST}/api/v3")


def _load_app_options(env: Env):
    from octokit.utils import get_json_data as octokit_get_json_data

    global APP_NAME, APP_DESCRIPTION, APP_ORGANIZATION, APP_PUBLIC
    global APP_DEFAULT_EVENTS, APP_DEFAULT_PERMISSIONS

    valid_events = octokit_get_json_data("events.json")

    with env.prefixed("APP_"):
        APP_NAME = env.str("NAME", "gh-app")
        APP_DESCRIPTION = env.str("DESCRIPTION", "")
        APP_ORGANIZATION = env.str("ORGANIZATION", None)
        APP_PUBLIC = env.bool("PUBLIC", True)
        with env.prefixed("DEFAULT_"):
            APP_DEFAULT_EVENTS = env.list(
                "EVENTS", "public", validate=ContainsOnly(valid_events)
            )
            APP_DEFAULT_PERMISSIONS = env.dict("PERMISSIONS", "metadata=read")


def _load_app_registration_options(env: Env):
    """
    TODO: decrypt these with Credstash, SecretsManager, or ParameterStore.
      ref: https://github.com/aws/chalice/issues/859#issuecomment-547676237
      ref: https://environ-config.readthedocs.io/en/stable/tutorial.html
      ref: https://bit.ly/why-you-shouldnt-use-env-variables-for-secret-data
    :param env:
    :return:
    """
    global APP_ID, APP_CLIENT_ID, APP_CLIENT_SECRET, APP_PEM, APP_WEBHOOK_SECRET
    with env.prefixed("APP_"):
        APP_ID = env.str("ID", None)
        APP_CLIENT_ID = env.str("CLIENT_ID", None)
        APP_CLIENT_SECRET = env.str("CLIENT_SECRET", None)
        APP_PEM = env.str("PEM", None)
        APP_WEBHOOK_SECRET = env.str("WEBHOOK_SECRET", None)


def save_app_registration(registration: Dict):
    # TODO: encrypt these in Credstash, SecretsManager, or ParameterStore
    # dotenv backing store (create if not exists)
    if not os.path.exists(".env"):
        f = open(".env", "w")
        f.close()

    keys = ["id", "client_id", "client_secret", "html_url", "pem", "webhook_secret"]
    for key in keys:
        set_key(".env", f"APP_{key.upper()}", str(registration[key]))

    env = Env()
    env.read_env(".env")
    _load_app_registration_options(env)
