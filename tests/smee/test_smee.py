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


@pytest.mark.parametrize(
    "stream,exit_code",
    [
        (
            "\n".join(
                [
                    "event:ready\ndata:{}\n",
                    "event:ping\ndata:{}\n",
                    'data:{"body":{},"timestamp":1,"query":{}}\n\n',
                ]
            ),
            0,
        ),
    ],
)
def test_command_line_interface(stream, exit_code, requests_mock):
    """Test the SMEE CLI."""
    runner = CliRunner()
    requests_mock.get("mock://smee.io/new", text=stream)
    requests_mock.post("mock://target.io/events")
    help_result = runner.invoke(
        cli.smee, ["--url=mock://smee.io/new", "--target=mock://target.io/events"]
    )
    assert help_result.exit_code == 0
    assert "Connected mock://smee.io/new" in help_result.output
