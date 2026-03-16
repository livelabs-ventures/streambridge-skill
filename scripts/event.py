#!/usr/bin/env python3
"""Event operations for the StreamBridge skill."""

from __future__ import annotations

import argparse
import sys

from streambridge_api import StreamBridgeClient, StreamBridgeError, jsonapi_resource, print_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Operate on StreamBridge events")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create")
    create_parser.add_argument("--name", required=True)

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("event_id")

    subparsers.add_parser("list")

    args = parser.parse_args()
    client = StreamBridgeClient()

    try:
        if args.command == "create":
            print_json({"event": jsonapi_resource(client.create_event(args.name))})
        elif args.command == "show":
            print_json({"event": jsonapi_resource(client.get_event(args.event_id))})
        else:
            print_json(client.list_events())
        return 0
    except StreamBridgeError as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
