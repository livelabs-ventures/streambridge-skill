#!/usr/bin/env python3
"""Validate auth and API connectivity for the StreamBridge skill."""

from __future__ import annotations

import sys

from streambridge_api import StreamBridgeClient, StreamBridgeError, auth_path, jsonapi_resource, print_json


def main() -> int:
    client = StreamBridgeClient()

    try:
        me = jsonapi_resource(client.auth_me())
    except StreamBridgeError as exc:
        print_json(
            {
                "ok": False,
                "api_base": client.api_base,
                "token_present": bool(client.token),
                "local_settings_path": auth_path(),
                "error": str(exc),
            }
        )
        return 1

    print_json(
        {
            "ok": True,
            "api_base": client.api_base,
            "token_present": True,
            "token_source": client.token_source,
            "local_settings_path": auth_path(),
            "user": me,
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
