#!/usr/bin/env python3
"""Sponsor (campaign) operations for the StreamBridge skill.

Mirrors the `bash scripts/streambridge sponsors ...` surface so agents that
prefer Python one-shots can manage event sponsors directly. Both layers call
the same Rails endpoint group and share the multipart upload helper in
`streambridge_api.py`.
"""

from __future__ import annotations

import argparse
import sys

from streambridge_api import (
    StreamBridgeClient,
    StreamBridgeError,
    jsonapi_resource,
    print_json,
)


def _slug_from_name(name: str) -> str:
    """Default ad_tag derivation when --on is omitted. Mirrors the Rails
    Campaign validator's accepted shape (a-z0-9_-)."""
    out: list[str] = []
    prev_underscore = False
    for ch in name.lower():
        if ch.isalnum():
            out.append(ch)
            prev_underscore = False
        elif not prev_underscore:
            out.append("_")
            prev_underscore = True
    return "".join(out).strip("_")


def _add_asset_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--logo", help="Path to logo asset (≤1MB, png/jpg/webp/svg)")
    parser.add_argument(
        "--mobile",
        help="Path to mobile banner (≤2MB, png/jpg/webp). Wide aspect, left-anchored.",
    )
    parser.add_argument(
        "--pillar",
        help="Path to pillar banner (≤5MB, png/jpg/webp). Portrait, full-bleed.",
    )


def _files_dict(args: argparse.Namespace) -> dict[str, str | None]:
    return {
        "logo": args.logo,
        "banner_mobile": args.mobile,
        "banner_pillar": args.pillar,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Manage StreamBridge event sponsors")
    sub = parser.add_subparsers(dest="command", required=True)

    list_p = sub.add_parser("list", help="List all sponsors on an event")
    list_p.add_argument("event_id")

    show_p = sub.add_parser("show", help="Show one sponsor (by name or id)")
    show_p.add_argument("event_id")
    show_p.add_argument("sponsor", help="Sponsor name or id")

    add_p = sub.add_parser("add", help="Create a sponsor")
    add_p.add_argument("event_id")
    add_p.add_argument("name", help="Sponsor display name (e.g. 'Cell C')")
    add_p.add_argument("--on", help="Camera ad_tag this sponsor binds to (default: slug of name)")
    add_p.add_argument("--link", required=True, help="Click-through URL")
    add_p.add_argument("--alt-text", help="Accessible alt text (defaults to the sponsor name)")
    _add_asset_args(add_p)
    add_p.add_argument(
        "--inactive",
        action="store_true",
        help="Create the sponsor in a paused state (default: active)",
    )

    set_p = sub.add_parser("set", help="Update any field on an existing sponsor")
    set_p.add_argument("event_id")
    set_p.add_argument("sponsor", help="Sponsor name or id")
    set_p.add_argument("--name", help="Rename the sponsor")
    set_p.add_argument("--on", help="Move the sponsor to a different camera tag")
    set_p.add_argument("--link", help="Update the click-through URL")
    set_p.add_argument("--alt-text", help="Update the alt text")
    _add_asset_args(set_p)
    set_p.add_argument("--active", action="store_true")
    set_p.add_argument("--inactive", action="store_true")

    swap_p = sub.add_parser("replace-asset", help="Swap one asset on an existing sponsor")
    swap_p.add_argument("event_id")
    swap_p.add_argument("sponsor", help="Sponsor name or id")
    _add_asset_args(swap_p)

    pause_p = sub.add_parser("pause", help="Deactivate a sponsor (hide the banner)")
    pause_p.add_argument("event_id")
    pause_p.add_argument("sponsor", help="Sponsor name or id")

    resume_p = sub.add_parser("resume", help="Reactivate a sponsor (show the banner)")
    resume_p.add_argument("event_id")
    resume_p.add_argument("sponsor", help="Sponsor name or id")

    rm_p = sub.add_parser("remove", help="Delete a sponsor")
    rm_p.add_argument("event_id")
    rm_p.add_argument("sponsor", help="Sponsor name or id")

    args = parser.parse_args()
    client = StreamBridgeClient()

    try:
        if args.command == "list":
            print_json(client.list_campaigns(args.event_id))

        elif args.command == "show":
            sid = client.resolve_campaign(args.event_id, args.sponsor)
            print_json({"sponsor": jsonapi_resource(client.get_campaign(args.event_id, sid))})

        elif args.command == "add":
            tag = args.on or _slug_from_name(args.name)
            fields: dict[str, str] = {
                "sponsor_name": args.name,
                "campaign_name": args.name,
                "tag": tag,
                "click_through_url": args.link,
                "alt_text": args.alt_text or args.name,
                "active": "false" if args.inactive else "true",
            }
            print_json(
                {"sponsor": jsonapi_resource(client.create_campaign(args.event_id, fields, _files_dict(args)))}
            )

        elif args.command == "set":
            sid = client.resolve_campaign(args.event_id, args.sponsor)
            fields: dict[str, str] = {}
            if args.name is not None:
                fields["sponsor_name"] = args.name
            if args.on is not None:
                fields["tag"] = args.on
            if args.link is not None:
                fields["click_through_url"] = args.link
            if args.alt_text is not None:
                fields["alt_text"] = args.alt_text
            if args.active:
                fields["active"] = "true"
            if args.inactive:
                fields["active"] = "false"
            files = _files_dict(args)
            if not fields and not any(files.values()):
                parser.error("Pass at least one field to update (e.g. --logo path or --link url)")
            print_json(
                {"sponsor": jsonapi_resource(client.update_campaign(args.event_id, sid, fields, files))}
            )

        elif args.command == "replace-asset":
            sid = client.resolve_campaign(args.event_id, args.sponsor)
            files = _files_dict(args)
            if not any(files.values()):
                parser.error("Pass at least one asset (--logo, --mobile, --pillar)")
            print_json(
                {"sponsor": jsonapi_resource(client.update_campaign(args.event_id, sid, None, files))}
            )

        elif args.command in ("pause", "resume"):
            sid = client.resolve_campaign(args.event_id, args.sponsor)
            fields = {"active": "true" if args.command == "resume" else "false"}
            print_json(
                {"sponsor": jsonapi_resource(client.update_campaign(args.event_id, sid, fields, None))}
            )

        elif args.command == "remove":
            sid = client.resolve_campaign(args.event_id, args.sponsor)
            client.delete_campaign(args.event_id, sid)
            print_json({"ok": True, "removed": sid})

    except StreamBridgeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
