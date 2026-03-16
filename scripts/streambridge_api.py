#!/usr/bin/env python3
"""Stdlib StreamBridge API client for the customer-facing skill."""

from __future__ import annotations

import json
import os
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_API_BASE = "https://api.streambridge.live/api/v1"
CONFIG_DIR = os.path.expanduser("~/.streambridge")
AUTH_PATH = os.path.join(CONFIG_DIR, "auth.json")


class StreamBridgeError(RuntimeError):
    """Raised when the StreamBridge API returns an error."""


def auth_path() -> str:
    return AUTH_PATH


def load_saved_token() -> str | None:
    try:
        with open(AUTH_PATH, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError):
        return None

    token = payload.get("api_token")
    return token.strip() if isinstance(token, str) and token.strip() else None


def save_token(token: str) -> str:
    os.makedirs(CONFIG_DIR, mode=0o700, exist_ok=True)
    try:
        os.chmod(CONFIG_DIR, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
    except OSError:
        pass

    temp_path = f"{AUTH_PATH}.tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump({"api_token": token}, handle)

    os.replace(temp_path, AUTH_PATH)
    try:
        os.chmod(AUTH_PATH, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass
    return AUTH_PATH


def prompt_for_token() -> str | None:
    if not sys.stdin.isatty():
        return None

    try:
        import getpass

        token = getpass.getpass("StreamBridge API token: ").strip()
    except (EOFError, KeyboardInterrupt):
        raise StreamBridgeError("Token entry cancelled") from None

    if not token:
        raise StreamBridgeError("No API token entered")

    save_token(token)
    return token


class StreamBridgeClient:
    def __init__(self, api_base: str | None = None, token: str | None = None) -> None:
        self.api_base = (api_base or os.environ.get("STREAMBRIDGE_API_BASE") or DEFAULT_API_BASE).rstrip("/")
        self.token = token or os.environ.get("STREAMBRIDGE_API_TOKEN") or load_saved_token()
        self.token_source = "argument" if token else "environment" if os.environ.get("STREAMBRIDGE_API_TOKEN") else "local_settings" if self.token else None

    def ensure_token(self) -> None:
        if not self.token:
            prompted_token = prompt_for_token()
            if prompted_token:
                self.token = prompted_token
                self.token_source = "local_settings"

        if not self.token:
            raise StreamBridgeError(
                f"No StreamBridge API token found. Run this command interactively to save one to {AUTH_PATH} or set STREAMBRIDGE_API_TOKEN."
            )

    def auth_me(self) -> dict[str, Any]:
        return self.request("GET", "/auth/me")

    def list_events(self) -> dict[str, Any]:
        return self.request("GET", "/events")

    def get_event(self, event_id: str) -> dict[str, Any]:
        return self.request("GET", f"/events/{event_id}")

    def create_event(self, name: str, is_default: bool = False) -> dict[str, Any]:
        return self.request("POST", "/events", {"event": {"name": name, "is_default": is_default}})

    def list_streams(self, event_id: str | None = None) -> dict[str, Any]:
        query = ""
        if event_id:
            query = "?" + urllib.parse.urlencode({"event_id": event_id})
        return self.request("GET", f"/streams{query}")

    def get_stream(self, stream_id: str) -> dict[str, Any]:
        return self.request("GET", f"/streams/{stream_id}")

    def create_stream(self, event_id: str, name: str, protocol: str = "srt", auto_start: bool = False) -> dict[str, Any]:
        return self.request(
            "POST",
            "/streams",
            {
                "stream": {
                    "event_id": event_id,
                    "name": name,
                    "protocol": protocol,
                    "auto_start": auto_start,
                }
            },
        )

    def start_stream(self, stream_id: str) -> dict[str, Any]:
        return self.request("POST", f"/streams/{stream_id}/start")

    def stop_stream(self, stream_id: str) -> dict[str, Any]:
        return self.request("POST", f"/streams/{stream_id}/stop")

    def get_stream_invite(self, stream_id: str) -> dict[str, Any]:
        return self.request("GET", f"/public/streams/{stream_id}/invite-url", require_auth=False)

    def get_event_page(self, event_id: str) -> dict[str, Any]:
        return self.request("GET", f"/events/{event_id}/page")

    def create_event_page(self, event_id: str, generation_prompt: str | None = None, starter_kit: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"event_page": {}}
        if generation_prompt:
            payload["event_page"]["generation_prompt"] = generation_prompt
        if starter_kit:
            payload["event_page"]["starter_kit"] = starter_kit
        return self.request("POST", f"/events/{event_id}/page", payload)

    def build_workspace(self, event_id: str) -> dict[str, Any]:
        return self.request("POST", f"/events/{event_id}/workspace/build")

    def preview_workspace(self, event_id: str) -> dict[str, Any]:
        return self.request("GET", f"/events/{event_id}/workspace/preview")

    def publish_event_page(self, event_id: str) -> dict[str, Any]:
        return self.request("POST", f"/events/{event_id}/page/publish", {})

    def get_event_page_versions(self, event_id: str) -> dict[str, Any]:
        return self.request("GET", f"/events/{event_id}/page/versions")

    def switch_featured_camera(self, event_id: str, camera_identity: str) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/events/{event_id}/live/featured_camera",
            {"camera_identity": camera_identity},
        )

    def send_notification(self, event_id: str, title: str, message: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"title": title}
        if message:
            payload["message"] = message
        return self.request("POST", f"/events/{event_id}/live/notification", payload)

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        require_auth: bool = True,
    ) -> dict[str, Any]:
        if require_auth:
            self.ensure_token()

        url = f"{self.api_base}{path}"
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(url, data=data, method=method)
        request.add_header("Accept", "application/json")

        if payload is not None:
            request.add_header("Content-Type", "application/json")

        if require_auth and self.token:
            request.add_header("Authorization", f"Bearer {self.token}")

        try:
            with urllib.request.urlopen(request) as response:
                body = response.read()
                return json.loads(body.decode("utf-8")) if body else {}
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8")
            message = body

            try:
                parsed = json.loads(body)
                error = parsed.get("error")
                if isinstance(error, dict):
                    message = error.get("message", body)
                elif error:
                    message = str(error)
            except json.JSONDecodeError:
                pass

            raise StreamBridgeError(f"{exc.code} {message}") from exc
        except urllib.error.URLError as exc:
            raise StreamBridgeError(f"Unable to reach StreamBridge API: {exc.reason}") from exc


def jsonapi_resource(document: dict[str, Any]) -> dict[str, Any]:
    resource = document.get("data", document)
    if resource is None:
        return {}

    if "attributes" not in resource:
        return resource

    flattened = {"id": resource.get("id")}
    flattened.update(resource.get("attributes", {}))
    return flattened


def print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2))
