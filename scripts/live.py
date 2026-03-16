#!/usr/bin/env python3
"""Live control operations for the StreamBridge skill."""

from __future__ import annotations

import argparse
import sys

from streambridge_api import StreamBridgeClient, StreamBridgeError, print_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Operate on a live StreamBridge event")
    subparsers = parser.add_subparsers(dest="command", required=True)

    switch_parser = subparsers.add_parser("switch-camera")
    switch_parser.add_argument("event_id")
    switch_parser.add_argument("--camera", required=True)

    notification_parser = subparsers.add_parser("notification")
    notification_parser.add_argument("event_id")
    notification_parser.add_argument("--title", required=True)
    notification_parser.add_argument("--message")

    args = parser.parse_args()
    client = StreamBridgeClient()

    try:
        if args.command == "switch-camera":
            print_json(client.switch_featured_camera(args.event_id, args.camera))
        else:
            print_json(client.send_notification(args.event_id, args.title, args.message))
        return 0
    except StreamBridgeError as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
