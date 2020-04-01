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

"""Webhook data delivery client. Please visit https://smee.io for more information."""
from dataclasses import dataclass

import requests

from . import event_stream


@dataclass
class SmeeClient(object):
    response: requests.Response
    target_url: str

    def run(self):
        callbacks = {
            None: self.on_payload,
            "ping": self.on_ping,
            "ready": self.on_ready,
        }
        for event in self.response.iter_events():
            callbacks[event.type](event)

    def on_ping(self, event):
        print(f"{self.response.url} is still alive...")

    def on_ready(self, event):
        print(f"Connected {self.response.url}")

    def on_payload(self, event: event_stream.Event):
        smee_event = event.json()
        body = smee_event.pop("body")
        _ = smee_event.pop("query")
        _ = smee_event.pop("timestamp")
        try:
            requests.post(self.target_url, json=body, headers=smee_event)
        except Exception:
            pass


def connect(webhook_proxy, target):
    events = event_stream.get(webhook_proxy)
    return SmeeClient(events, target)
