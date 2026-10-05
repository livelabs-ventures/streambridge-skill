#!/usr/bin/env python3
"""One-shot Streamable HTTP MCP client. No retries of mutating tool calls."""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
import urllib.error
import urllib.request
from typing import Any

from streambridge_api import StreamBridgeClient, StreamBridgeError, print_json


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class McpClient:
    def __init__(self, url: str, token: str) -> None:
        self.url = url
        self.token = token
        self.session_id: str | None = None
        self.protocol = "2025-11-25"
        self.opener = urllib.request.build_opener(NoRedirect())

    def request(self, method: str, params: dict[str, Any], request_id: int | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method, "params": params}
        if request_id is not None:
            payload["id"] = request_id
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "MCP-Protocol-Version": self.protocol,
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        req = urllib.request.Request(self.url, data=json.dumps(payload).encode(), headers=headers, method="POST")
        try:
            with self.opener.open(req, timeout=30) as response:
                self.session_id = response.headers.get("Mcp-Session-Id", self.session_id)
                if request_id is None:
                    return {}
                if response.headers.get_content_type() == "text/event-stream":
                    result = self.read_event(response, request_id)
                else:
                    result = json.load(response)
        except urllib.error.HTTPError as exc:
            raise StreamBridgeError(f"MCP HTTP {exc.code}; check endpoint, grant and enabled features") from None
        except (urllib.error.URLError, socket.timeout, OSError):
            raise StreamBridgeError("MCP connection failed or timed out; inspect state before retrying writes") from None
        except (json.JSONDecodeError, UnicodeDecodeError):
            raise StreamBridgeError("MCP returned an invalid JSON response") from None
        if not isinstance(result, dict) or result.get("id") != request_id:
            raise StreamBridgeError("MCP response did not match the request")
        if "error" in result:
            error = result["error"]
            code = error.get("code", "unknown") if isinstance(error, dict) else "unknown"
            raise StreamBridgeError(f"MCP JSON-RPC error {code}")
        if not isinstance(result.get("result"), dict):
            raise StreamBridgeError("MCP response has no result object")
        return result["result"]

    @staticmethod
    def read_event(response: Any, request_id: int) -> dict[str, Any]:
        data: list[str] = []
        for raw in response:
            line = raw.decode("utf-8").rstrip("\r\n")
            if line.startswith("data:"):
                data.append(line[5:].removeprefix(" "))
            elif not line and data:
                message = json.loads("\n".join(data))
                data = []
                if isinstance(message, dict) and message.get("id") == request_id:
                    return message
        raise StreamBridgeError("MCP stream ended without a matching response")

    def initialize(self) -> None:
        result = self.request("initialize", {
            "protocolVersion": self.protocol,
            "capabilities": {},
            "clientInfo": {"name": "streambridge-skill-cli", "version": "2.0"},
        }, 1)
        protocol = result.get("protocolVersion")
        if protocol not in {"2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"}:
            raise StreamBridgeError("MCP returned an unsupported protocol version")
        self.protocol = protocol
        self.request("notifications/initialized", {})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["legacy", "host"], default="legacy")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("tools", aliases=["list"])
    call = commands.add_parser("call")
    call.add_argument("tool")
    call.add_argument("arguments", nargs="?", default="{}")
    args = parser.parse_args()
    # Validate before authentication or any network request.
    arguments = {}
    if args.command == "call":
        try:
            arguments = json.loads(args.arguments)
        except json.JSONDecodeError:
            parser.error("tool arguments must be valid JSON")
        if not isinstance(arguments, dict):
            parser.error("tool arguments must be a JSON object")
    try:
        api = StreamBridgeClient()
        if args.profile == "host":
            token = os.environ.get("STREAMBRIDGE_HOST_TOKEN", "").strip()
            if not token:
                raise StreamBridgeError("Set STREAMBRIDGE_HOST_TOKEN to an OAuth grant for /mcp/chatgpt. PATs cannot authorize the host profile.")
            path = "/mcp/chatgpt"
        else:
            api.ensure_token()
            token = api.token
            path = "/mcp"
        url = os.environ.get("STREAMBRIDGE_MCP_URL") or api.api_base.removesuffix("/api/v1") + path
        client = McpClient(url, token)
        client.initialize()
        result = client.request(
            "tools/call" if args.command == "call" else "tools/list",
            {"name": args.tool, "arguments": arguments} if args.command == "call" else {},
            2,
        )
        print_json(result)
        return 1 if result.get("isError") else 0
    except StreamBridgeError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
