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
import pytest
from click.testing import CliRunner

from zeroae.smee import cli


@pytest.fixture()
def smee_server_mock(requests_mock):
    url = "mock://smee.io/new"
    requests_mock.get(
        url,
        text="\n".join(
            [
                "event:ready\ndata:{}\n",
                "event:ping\ndata:{}\n",
                'data:{"body":{},"timestamp":1,"query":{}}\n\n',
            ]
        ),
    )
    return url


def test_command_line_interface(smee_server_mock, requests_mock):
    """Test the SMEE CLI."""
    runner = CliRunner()
    args = [f"--url={smee_server_mock}"]

    target_url = "mock://target.io/events"
    requests_mock.post(target_url)
    args += [f"--target={target_url}"]

    help_result = runner.invoke(cli.smee, args)
    assert help_result.exit_code == 0
    assert f"Connected {smee_server_mock}" in help_result.output


@pytest.mark.parametrize(
    "port,path", [(None, None), (6000, None), (None, "/events"), (6000, "/events")]
)
def test_command_line_interface_port_path(port, path, smee_server_mock, requests_mock):
    """Test the SMEE CLI."""
    runner = CliRunner()
    args = [f"--url={smee_server_mock}"]

    if port is None:
        port = 3000
    else:
        args += [f"--port={port}"]

    if path is None:
        path = "/"
    else:
        args += [f"--path={path}"]

    target_url = f"http://127.0.0.1:{port}{path}"
    requests_mock.post(target_url)

    help_result = runner.invoke(cli.smee, args)
    assert help_result.exit_code == 0
    assert f"Connected {smee_server_mock}" in help_result.output
