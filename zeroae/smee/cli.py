# ------------------------------------------------------------------------------
#  Copyright (c) 2020 Zero A.E., LLC.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ------------------------------------------------------------------------------

from urllib.parse import urljoin

import click
import click_log

from zeroae.smee import SmeeClient, logger

click_log.basic_config(logger)


@click.command(name="smee")
@click.version_option("0.0.1")
@click.option(
    "-u",
    "--url",
    help="URL of the webhook proxy service.",
    default="https://smee.io/new",
    show_default=True,
    envvar="WEBHOOK_PROXY",
)
@click.option(
    "-t",
    "--target",
    help="Full URL (including protocol and path) of the target service the events will be "
    "forwarded to. [default: http://127.0.0.1:{port}/{path}]",
)
@click.option(
    "-p", "--port", help="Local HTTP server port", default=3000, show_default=True
)
@click.option(
    "-P",
    "--path",
    help="URL path to post proxied requests to",
    default="/",
    show_default=True,
)
@click_log.simple_verbosity_option(logger, "-l", "--logging", show_default=True)
def smee(url, target, port, path):
    """
    Webhook data delivery client.

    Please visit https://smee.io for more information.
    """
    if target is None:
        target = urljoin(f"http://127.0.0.1:{port}/", path)

    client = SmeeClient(source=url, target=target)
    logger.info(f"Forwarding {client.source} to {target}")
    client.run()
