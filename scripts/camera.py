#!/usr/bin/env python3
"""Camera operations for the StreamBridge skill."""

from __future__ import annotations

import argparse
import sys

from streambridge_api import StreamBridgeClient, StreamBridgeError, jsonapi_resource, print_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Operate on StreamBridge cameras")
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("event_id")
    add_parser.add_argument("--name", required=True)
    add_parser.add_argument("--protocol", default="srt")
    add_parser.add_argument("--start", action="store_true")
    add_parser.add_argument("--hidden", action="store_true")

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("event_id")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("stream_id")

    start_parser = subparsers.add_parser("start")
    start_parser.add_argument("stream_id")

    stop_parser = subparsers.add_parser("stop")
    stop_parser.add_argument("stream_id")

    invite_parser = subparsers.add_parser("invite")
    invite_parser.add_argument("stream_id")

    visibility_parser = subparsers.add_parser("visibility")
    visibility_parser.add_argument("stream_id")
    visibility_group = visibility_parser.add_mutually_exclusive_group(required=True)
    visibility_group.add_argument("--public", action="store_true")
    visibility_group.add_argument("--hidden", action="store_true")

    args = parser.parse_args()
    client = StreamBridgeClient()

    try:
        if args.command == "add":
            stream = jsonapi_resource(client.create_stream(args.event_id, args.name, protocol=args.protocol, publicly_visible=not args.hidden))
            if args.start:
                stream = jsonapi_resource(client.start_stream(stream["id"]))
            print_json({"stream": stream})
        elif args.command == "list":
            print_json(client.list_streams(args.event_id))
        elif args.command == "show":
            print_json({"stream": jsonapi_resource(client.get_stream(args.stream_id))})
        elif args.command == "start":
            print_json({"stream": jsonapi_resource(client.start_stream(args.stream_id))})
        elif args.command == "stop":
            print_json({"stream": jsonapi_resource(client.stop_stream(args.stream_id))})
        elif args.command == "visibility":
            print_json({"stream": jsonapi_resource(client.update_stream_visibility(args.stream_id, args.public))})
        else:
            print_json(client.get_stream_invite(args.stream_id))
        return 0
    except StreamBridgeError as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
