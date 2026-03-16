#!/usr/bin/env python3
"""Create an event, cameras, invites, and page setup in one flow."""

from __future__ import annotations

import argparse
import re
import sys
from typing import Any

from streambridge_api import StreamBridgeClient, StreamBridgeError, jsonapi_resource, print_json


def infer_event_name(description: str, template: str | None) -> str:
    cleaned = re.sub(r"\s+", " ", description).strip()
    if template == "news" and cleaned.lower().startswith("breaking"):
        return cleaned[:80]

    words = cleaned.split()
    return " ".join(words[:8])[:80] if words else "StreamBridge Event"


def default_camera_names(template: str | None, count: int) -> list[str]:
    template_names = {
        "sports": ["Touchline", "Scoreboard", "Crowd"],
        "race": ["Start", "Checkpoint", "Finish"],
        "news": ["Field Camera 1", "Field Camera 2", "Field Camera 3"],
    }
    base_names = template_names.get(template or "", [])

    if len(base_names) >= count:
        return base_names[:count]

    names = base_names[:]
    while len(names) < count:
        names.append(f"Camera {len(names) + 1}")
    return names


def create_page(client: StreamBridgeClient, event_id: str, description: str, template: str | None) -> dict[str, Any]:
    try:
        return client.create_event_page(event_id, generation_prompt=description, starter_kit=template)
    except StreamBridgeError as exc:
        if "already has a page" in str(exc).lower():
            return client.get_event_page(event_id)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the StreamBridge quickstart flow")
    parser.add_argument("description", help="Describe the event you want to set up")
    parser.add_argument("--template", choices=["sports", "race", "news"])
    parser.add_argument("--event-name")
    parser.add_argument("--camera-count", type=int, default=3)
    parser.add_argument("--camera-name", action="append", dest="camera_names")
    parser.add_argument("--publish", action="store_true")
    parser.add_argument("--no-publish", action="store_true")
    args = parser.parse_args()

    if args.publish and args.no_publish:
        print_json({"ok": False, "error": "Choose either --publish or --no-publish, not both"})
        return 1

    client = StreamBridgeClient()
    event_name = args.event_name or infer_event_name(args.description, args.template)
    camera_names = args.camera_names or default_camera_names(args.template, args.camera_count)

    try:
        event = jsonapi_resource(client.create_event(event_name))
        event_id = event["id"]
        streams = []

        for name in camera_names:
            stream = jsonapi_resource(client.create_stream(event_id, name))
            started = jsonapi_resource(client.start_stream(stream["id"]))
            invite = client.get_stream_invite(stream["id"])
            streams.append(
                {
                    "stream": started,
                    "invite": invite,
                }
            )

        page = jsonapi_resource(create_page(client, event_id, args.description, args.template))
        build = client.build_workspace(event_id)
        preview = client.preview_workspace(event_id)

        result: dict[str, Any] = {
            "event": event,
            "streams": streams,
            "page": page,
            "build": build,
            "preview": preview,
            "publish_required_confirmation": not args.publish and not args.no_publish,
        }

        if args.publish:
            result["published"] = jsonapi_resource(client.publish_event_page(event_id))

        print_json(result)
        return 0
    except StreamBridgeError as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
