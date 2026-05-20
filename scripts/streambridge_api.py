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
import uuid as _uuid
from typing import Any, Iterable


DEFAULT_API_BASE = "https://api.streambridge.live/api/v1"
CONFIG_DIR = os.path.expanduser("~/.streambridge")
AUTH_PATH = os.path.join(CONFIG_DIR, "auth.json")

# Asset upload helpers — mirrors the Rails Campaign budgets so we can fail
# fast on the client instead of round-tripping for a 422.
_CONTENT_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def _guess_content_type(path: str) -> str:
    return _CONTENT_TYPES.get(os.path.splitext(path)[1].lower(), "application/octet-stream")


def _build_multipart(
    fields: dict[str, Any],
    files: Iterable[tuple[str, str | None]],
) -> tuple[bytes, str]:
    """Build a multipart/form-data body from scalar fields + file paths.

    Stdlib-only — the public skill avoids a `requests` dependency so it runs
    on a clean Python install. The Rails campaigns endpoint accepts logo,
    banner_mobile, and banner_pillar as ActiveStorage attachments alongside
    scalar fields like sponsor_name and tag.
    """
    boundary = "----StreamBridgeBoundary" + _uuid.uuid4().hex
    parts: list[bytes] = []
    for name, value in fields.items():
        if value is None:
            continue
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        )
        parts.append(str(value).encode("utf-8"))
        parts.append(b"\r\n")
    for name, path in files:
        if not path:
            continue
        filename = os.path.basename(path)
        ctype = _guess_content_type(filename)
        with open(path, "rb") as handle:
            data = handle.read()
        parts.append(f"--{boundary}\r\n".encode())
        parts.append(
            (
                f'Content-Disposition: form-data; name="{name}"; '
                f'filename="{filename}"\r\n'
            ).encode()
        )
        parts.append(f"Content-Type: {ctype}\r\n\r\n".encode())
        parts.append(data)
        parts.append(b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


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

    # ------- Sponsor campaigns -------------------------------------------------
    # A "campaign" in the API is a sponsor row bound to an event. Public-skill
    # docs and the bash CLI surface this as "sponsor" (the organizer's word).

    def list_campaigns(self, event_id: str) -> dict[str, Any]:
        return self.request("GET", f"/events/{event_id}/campaigns")

    def get_campaign(self, event_id: str, campaign_id: str) -> dict[str, Any]:
        return self.request("GET", f"/events/{event_id}/campaigns/{campaign_id}")

    def delete_campaign(self, event_id: str, campaign_id: str) -> dict[str, Any]:
        return self.request("DELETE", f"/events/{event_id}/campaigns/{campaign_id}")

    def create_campaign(
        self,
        event_id: str,
        fields: dict[str, Any],
        files: dict[str, str | None] | None = None,
    ) -> dict[str, Any]:
        return self.request_multipart(
            "POST",
            f"/events/{event_id}/campaigns",
            fields,
            list((files or {}).items()),
        )

    def update_campaign(
        self,
        event_id: str,
        campaign_id: str,
        fields: dict[str, Any] | None = None,
        files: dict[str, str | None] | None = None,
    ) -> dict[str, Any]:
        return self.request_multipart(
            "PATCH",
            f"/events/{event_id}/campaigns/{campaign_id}",
            fields or {},
            list((files or {}).items()),
        )

    def resolve_campaign(self, event_id: str, key: str) -> str:
        """Map a sponsor name OR a uuid to a campaign id.

        Case-insensitive name match on `attributes.sponsor_name`. Raises
        StreamBridgeError with the candidate list when no match is found so
        callers (and agents reading the error) can self-correct.
        """
        if _looks_like_uuid(key):
            return key
        document = self.list_campaigns(event_id)
        wanted = key.lower()
        candidates: list[tuple[str, str]] = []
        for item in document.get("data", []) or []:
            attrs = item.get("attributes", {}) or {}
            sponsor_name = attrs.get("sponsor_name") or ""
            candidates.append((sponsor_name, item.get("id") or ""))
            if sponsor_name.lower() == wanted:
                return item.get("id") or ""
        listing = "\n".join(f"  - {name} ({cid})" for name, cid in candidates if cid)
        raise StreamBridgeError(
            f'No sponsor named "{key}" on event {event_id}.\n'
            f"Available sponsors:\n{listing or '  (none)'}"
        )

    def request_multipart(
        self,
        method: str,
        path: str,
        fields: dict[str, Any],
        files: list[tuple[str, str | None]],
    ) -> dict[str, Any]:
        self.ensure_token()
        body, content_type = _build_multipart(fields, files)
        url = f"{self.api_base}{path}"
        request = urllib.request.Request(url, data=body, method=method)
        request.add_header("Accept", "application/json")
        request.add_header("Content-Type", content_type)
        request.add_header("Content-Length", str(len(body)))
        if self.token:
            request.add_header("Authorization", f"Bearer {self.token}")
        try:
            with urllib.request.urlopen(request) as response:
                data = response.read()
                return json.loads(data.decode("utf-8")) if data else {}
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8")
            message = error_body
            try:
                parsed = json.loads(error_body)
                error = parsed.get("error")
                if isinstance(error, dict):
                    message = error.get("message", error_body)
                    errors = error.get("errors")
                    if errors:
                        message = f"{message}: {', '.join(errors)}"
                elif error:
                    message = str(error)
            except json.JSONDecodeError:
                pass
            raise StreamBridgeError(f"{exc.code} {message}") from exc
        except urllib.error.URLError as exc:
            raise StreamBridgeError(f"Unable to reach StreamBridge API: {exc.reason}") from exc

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


_UUID_RE = (
    "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    "[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def _looks_like_uuid(value: str) -> bool:
    import re as _re

    return bool(_re.match(_UUID_RE, value))


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
