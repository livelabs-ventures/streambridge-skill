#!/usr/bin/env python3
"""Event page operations for the StreamBridge skill."""

from __future__ import annotations

import argparse
import sys

from streambridge_api import StreamBridgeClient, StreamBridgeError, jsonapi_resource, print_json


def main() -> int:
    parser = argparse.ArgumentParser(description="Operate on StreamBridge event pages")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("event_id")
    init_parser.add_argument("--prompt")
    init_parser.add_argument("--starter-kit")

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("event_id")

    build_parser = subparsers.add_parser("build")
    build_parser.add_argument("event_id")

    preview_parser = subparsers.add_parser("preview")
    preview_parser.add_argument("event_id")

    publish_parser = subparsers.add_parser("publish")
    publish_parser.add_argument("event_id")

    versions_parser = subparsers.add_parser("versions")
    versions_parser.add_argument("event_id")

    args = parser.parse_args()
    client = StreamBridgeClient()

    try:
        if args.command == "init":
            print_json(
                {
                    "page": jsonapi_resource(
                        client.create_event_page(
                            args.event_id,
                            generation_prompt=args.prompt,
                            starter_kit=args.starter_kit,
                        )
                    )
                }
            )
        elif args.command == "status":
            print_json({"page": jsonapi_resource(client.get_event_page(args.event_id))})
        elif args.command == "build":
            print_json(client.build_workspace(args.event_id))
        elif args.command == "preview":
            print_json(client.preview_workspace(args.event_id))
        elif args.command == "publish":
            print_json({"page": jsonapi_resource(client.publish_event_page(args.event_id))})
        else:
            print_json(client.get_event_page_versions(args.event_id))
        return 0
    except StreamBridgeError as exc:
        print_json({"ok": False, "error": str(exc)})
        return 1


if __name__ == "__main__":
    sys.exit(main())
