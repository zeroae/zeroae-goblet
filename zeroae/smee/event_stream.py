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

from dataclasses import dataclass

import requests
from requests.compat import json as complexjson


@dataclass
class Event:
    """
    Event class for text/event-stream.

    ref: https://html.spec.whatwg.org/multipage/server-sent-events.html
    """

    id: str = None
    event: str = "message"
    retry: int = 2 * 1_000
    _data: str = None

    @property
    def type(self) -> str:
        return self.event

    @property
    def data(self) -> str:
        return self._data

    @data.setter
    def data(self, v: str):
        self._data = v if self._data is None else "\n".join([self._data, v])

    def json(self, **kwargs):
        return complexjson.loads(self._data, **kwargs)


def session() -> requests.Session:
    """Return a request Session configured for processing an Event-Stream."""
    s = requests.Session()
    s.headers["Accept"] = "text/event-stream"
    s.stream = True
    return s


def get(url: str, **kwargs):
    """Sends a GET request that only accepts a text/event-stream source."""
    with session() as s:
        return s.get(url, **kwargs)


def iter_events(r: requests.models.Response) -> Event:
    """Iterates over the source data, one Event at a time.
    When stream=True is set on the request, this avoids reading the
    content at once into memory for large responses.
    .. note:: This method is not reentrant safe.
    """

    event = None
    r.encoding = r.encoding if r.encoding else "utf-8"
    for line in r.iter_lines(chunk_size=128, decode_unicode=True):
        if not line:
            if event is not None and event.data is not None:
                yield event
            event = None
        elif line.startswith(":"):
            # Ignore comments
            pass
        else:
            if event is None:
                event = Event()
            k, v = line.split(":", maxsplit=1) if ":" in line else (line, "")
            if hasattr(event, k):
                event.__setattr__(k, v[1:] if v.startswith(" ") else v)


requests.models.Response.iter_events = iter_events
