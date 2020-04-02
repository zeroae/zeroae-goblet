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

import textwrap
from http import HTTPStatus

import pytest

from zeroae.smee import event_stream
from zeroae.smee.event_stream import Event


def test_session():
    s = event_stream.session()
    assert s.headers["accept"] == "text/event-stream"
    assert s.stream


def test_get(requests_mock):
    requests_mock.get(
        "mock://smee.io/new", text="Hello World", status_code=HTTPStatus.OK
    )
    r = event_stream.get("mock://smee.io/new")
    assert r.text == "Hello World"


@pytest.mark.parametrize("stream,data", [(":this is a test\n\n", ""), (":🥇\n\n", "🥇")])
def test_no_event(stream, data, requests_mock):
    requests_mock.get("mock://smee.io/new", text=textwrap.dedent(stream))
    r = event_stream.get("mock://smee.io/new")
    events: list[Event] = list(r.iter_events())
    assert len(events) == 0


@pytest.mark.parametrize(
    "stream,data",
    [
        ("data\n\n", ""),
        ("data\ndata\n\n", "\n"),
        ("data:test\n\n", "test"),
        ("data: test\n\n", "test"),
        ("data:  test\n\n", " test"),
        ("data:test\n: This is a comment, ignore me!!!:::\n\n", "test"),
        ("data: YHOO\ndata: +2\ndata: 10\n\n", "YHOO\n+2\n10"),
    ],
)
def test_one_event(stream, data, requests_mock):
    requests_mock.get("mock://smee.io/new", text=textwrap.dedent(stream))
    r = event_stream.get("mock://smee.io/new")
    events: list[Event] = list(r.iter_events())
    assert len(events) == 1
    assert events[0].data == data
    assert events[0].type == "message"


@pytest.mark.parametrize(
    "stream,data", [("data: {}\n\n", {}), ('data: {"key":"🥇"}\n\n', {"key": "🥇"})],
)
def test_one_json_event(stream, data, requests_mock):
    requests_mock.get("mock://smee.io/new", text=textwrap.dedent(stream))
    r = event_stream.get("mock://smee.io/new")
    events: list[Event] = list(r.iter_events())
    assert len(events) == 1
    assert events[0].type == "message"
    assert events[0].json() == data
