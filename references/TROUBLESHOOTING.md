# StreamBridge Skill Troubleshooting

## REST authentication or connection

Run `bash scripts/streambridge doctor`. Use a valid PAT from Settings > API Tokens,
provided through `STREAMBRIDGE_API_TOKEN` or saved at `~/.streambridge/auth.json`.
To replace a saved token, remove that file and run interactively again.
REST base overrides accept an origin or `/api/v1` URL: `STREAMBRIDGE_API_BASE`,
`STREAMBRIDGE_API_BASE_URL`, or `STREAMBRIDGE_API_URL` (in that precedence).

## MCP failure

Python 3.10+ is required for MCP. `mcp` targets `/mcp` with the normal PAT.
`mcp --profile host` targets `/mcp/chatgpt` with only `STREAMBRIDGE_HOST_TOKEN`.
Check `STREAMBRIDGE_MCP_URL` if overriding either endpoint. Host grants require
OAuth resource/organization binding, pilot entitlement and enabled read/write
flags. A PAT or revoked grant yields 401; denied capabilities yield tool errors.
The CLI exits nonzero for HTTP, JSON-RPC and tool errors, including SSE responses.
After a timeout inspect state before retrying; reuse the same operation ID and
arguments for a host mutation retry. Read fresh revisions after an edit conflict.

## Setup succeeded but camera video is missing

A camera slot, invitation or `active` status does not verify video. Open the
management page, connect the phone/encoder and check actual media plus timestamps.
Inspect `streams show <stream-id>` and metrics before explicitly starting
processing. Quickstart creates slots without calling start by default.

## Quickstart failed partway through

Output retains completed event/camera IDs. Continue those resources with the
CLI; rerunning quickstart creates another event. An invitation failure does not
mean camera creation failed. No writes are automatically retried.

## Custom page publish failed

The default public page needs no publish call. For a requested custom page,
verify Director access, `page status <event-id>`, a successful build and preview.
Publish that existing event with `page publish <event-id>`.

## Device-authenticated commands

Create a fresh session with `public device-session <stream-key> <device-id>`.
Use its device token with `--device-token` or `STREAMBRIDGE_DEVICE_TOKEN` for
`public livekit`, `telemetry`, and `stream-metrics`. Keep tokens and invitation
URLs with the intended operators.

## Operation missing from wrappers

Read `API.md` and the applicable OpenAPI contract. Use `api <METHOD> <PATH> JSON`
for current REST endpoints or discover tools in the correct MCP profile.
