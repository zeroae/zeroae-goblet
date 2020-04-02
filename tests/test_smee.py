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

from click.testing import CliRunner

from zeroae.smee import cli


def test_command_line_interface():
    """Test the SMEE CLI."""
    runner = CliRunner()

    help_result = runner.invoke(cli.smee, ["--help"])
    assert help_result.exit_code == 0
    assert "Show this message and exit." in help_result.output
