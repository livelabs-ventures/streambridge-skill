# StreamBridge Public API Reference

Use this file when the bash CLI wrapper does not already expose the exact operation you need.

## Base URLs

- App docs: `https://app.streambridge.live/docs/mcp`
- API base: `https://api.streambridge.live/api/v1`
- MCP endpoint: `https://api.streambridge.live/mcp`
- Skill zip: `https://api.streambridge.live/downloads/streambridge-skill.zip`

## Preferred path

Use the bundled bash CLI first:

```bash
bash scripts/streambridge doctor
bash scripts/streambridge events list
bash scripts/streambridge streams create <event-id> "Touchline"
```

If the wrapper does not cover the operation you need:

```bash
bash scripts/streambridge api <METHOD> <PATH> '<json-body>'
bash scripts/streambridge mcp call <tool_name> '<json-args>'
```

## Authentication

Most `/api/v1/**` endpoints require a personal access token in:

```bash
Authorization: Bearer sb_pat_...
```

The CLI prompts for a token on first use and stores it in `~/.streambridge/auth.json`.

## Common API paths

### Auth tokens

- `GET /auth/tokens`
- `POST /auth/tokens`
- `DELETE /auth/tokens/:id`

### Events

- `GET /events`
- `GET /events/:id`
- `POST /events`
- `PATCH /events/:id`
- `DELETE /events/:id`

### Streams

- `GET /streams`
- `GET /streams/:id`
- `POST /streams`
- `PATCH /streams/:id`
- `DELETE /streams/:id`
- `POST /streams/:id/start`
- `POST /streams/:id/stop`
- `GET /streams/:id/metrics`

### Event pages

- `GET /events/:event_id/page`
- `POST /events/:event_id/page`
- `PATCH /events/:event_id/page`
- `POST /events/:event_id/page/publish`
- `POST /events/:event_id/page/rollback`
- `GET /events/:event_id/page/versions`
- `GET /events/:event_id/workspace/files`
- `POST /events/:event_id/workspace/files`
- `PATCH /events/:event_id/workspace/files`
- `GET /events/:event_id/workspace/files/list`
- `POST /events/:event_id/workspace/build`
- `GET /events/:event_id/workspace/preview`
- `GET /public/events/:event_id/workspace/render`
- `GET /public/events/:event_id/workspace/live`

### Live control

- `POST /events/:event_id/live/overlay`
- `POST /events/:event_id/live/leaderboard`
- `POST /events/:event_id/live/score`
- `POST /events/:event_id/live/notification`
- `POST /events/:event_id/live/featured_camera`
- `POST /events/:event_id/live/stats`

### Feedback

- `GET /feedback_items`
- `GET /feedback_items/roadmap`
- `GET /feedback_items/:id`
- `POST /feedback_items`
- `PATCH /feedback_items/:id`
- `DELETE /feedback_items/:id`
- `PATCH /feedback_items/:id/status`
- `PATCH /feedback_items/:id/priority`
- `PATCH /feedback_items/:id/duplicate`
- `GET /feedback_items/:feedback_item_id/comments`
- `POST /feedback_items/:feedback_item_id/comments`
- `POST /feedback_items/:feedback_item_id/vote`
- `DELETE /feedback_items/:feedback_item_id/vote`
- `POST /feedback_items/:feedback_item_id/follow`
- `DELETE /feedback_items/:feedback_item_id/follow`

### Public device and viewer endpoints

- `POST /public/events/:event_id/viewer_token`
- `GET /public/events/:event_id/sportraxs/races/:race_id/leaderboard`
- `GET /public/events/:event_id/sportraxs/races/:race_id/results`
- `GET /public/streams/:id/invite-url`
- `GET /public/streams/by-key/:stream_key`
- `POST /public/streams/by-key/:stream_key/device-session`
- `GET /public/streams/by-key/:stream_key/livekit`
- `POST /public/streams/by-key/:stream_key/telemetry`
- `POST /public/streams/by-key/:stream_key/stream-metrics`

## Common payload examples

### Create an event

```bash
bash scripts/streambridge api POST /events '{"event":{"name":"School Rugby Finals"}}'
```

### Create an API token

```bash
bash scripts/streambridge auth tokens create "Codex laptop" 2026-12-31T23:59:59Z
```

### Create a stream

```bash
bash scripts/streambridge api POST /streams '{"stream":{"event_id":"<event-id>","name":"Touchline","protocol":"srt"}}'
```

### Publish a page

```bash
bash scripts/streambridge api POST /events/<event-id>/page/publish '{}'
```

### Read a workspace file

```bash
bash scripts/streambridge page file-read <event-id> src/App.tsx
```

### Create feedback

```bash
bash scripts/streambridge api POST /feedback_items '{"feedback_item":{"kind":"feature_request","status":"open","title":"Add a lower third editor","description_markdown":"Need reusable lower-thirds for commentary.","context":{"source":"skill"}}}'
```

### Get device credentials then LiveKit credentials

```bash
bash scripts/streambridge public device-session <stream-key> <device-id>
bash scripts/streambridge public livekit <stream-key> --device-token <device-token>
```

### Call MCP directly

```bash
bash scripts/streambridge mcp tools
bash scripts/streambridge mcp call create_viewer_token '{"event_id":"<event-id>","viewer_name":"Viewer"}'
```

## Current MCP tools

The MCP tool set is narrower than the full REST API. When a route is not exposed as an MCP tool, use the bash CLI wrapper or direct REST fallback above.

- `list_events`
- `get_event`
- `create_event`
- `update_event`
- `delete_event`
- `list_streams`
- `get_stream`
- `create_stream`
- `start_stream`
- `stop_stream`
- `delete_stream`
- `get_stream_invite_url`
- `get_stream_metrics`
- `create_viewer_token`
