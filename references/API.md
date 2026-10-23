# StreamBridge Public API Reference

Use this file when the bash CLI wrapper does not already expose the exact operation you need.

## Base URLs

- App docs: `https://app.streambridge.live/docs/mcp`
- API base: `https://api.streambridge.live/api/v1`
- General operator MCP endpoint: `https://api.streambridge.live/mcp`
- Host OAuth MCP endpoint (gated pilot): `https://api.streambridge.live/mcp/chatgpt`
- Skill zip: `https://api.streambridge.live/downloads/streambridge-skill.zip`

## Preferred path

Use the bundled bash CLI first:

```bash
bash scripts/streambridge doctor
bash scripts/streambridge events list
bash scripts/streambridge streams create <event-id> "Finish Line"
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
- `POST /events/:event_id/programme` — idempotent optional programme preparation, without processing startup

Event list accepts `query`, `page`, `per_page` (max 100), `event_type`
(`all`, `default`, or `manual`), and `sort` (`newest`, `oldest`, `name_asc`, `name_desc`, `updated`).
Event writes use an `event` object. REST accepts `name`, `is_default`,
`template_key`, `shortcode`, `subtitle`, `description`, `starts_at`, `ends_at`,
`live_only`, `logo_in_header` (the event's logo top left on its public page, in
place of StreamBridge's, while it has a logo), and `onboarding`. `timezone` is supported by the scoped host API,
not the general event write endpoint.
The public page at `https://app.streambridge.live/v/<event-id>` exists on creation;
management is at `/events/<event-id>`.

### Streams

- `GET /streams`
- `GET /streams/:id`
- `POST /streams`
- `PATCH /streams/:id`
- `DELETE /streams/:id`
- `POST /streams/:id/start`
- `POST /streams/:id/stop`
- `GET /streams/:id/metrics`

### Camera invitations

- `GET /public/streams/:id/invite-url`

Despite the legacy `/public` path, issuing an invitation requires the host's
bearer token and a camera in the host's current organization. Both
`streams invite <stream-id>` and the compatibility alias `public invite <stream-id>`
send the saved host token. The Python client's `get_stream_invite` does the same.
Finished shows cannot receive camera invitations. Treat invitation URLs as
publishing credentials and share them only with the intended camera operator.

### Destinations and public event view

The current editor uses destinations as the page/layout contract:

- `GET /events/:event_id/destination`
- `GET /events/:event_id/destination/components`
- `GET /events/:event_id/destination/adapters`
- `GET /events/:event_id/destination/draft`
- `POST /events/:event_id/destination/draft/operations`
- `POST /events/:event_id/destination/draft/reset`
- `POST /events/:event_id/destination/publish`
- `PUT /events/:event_id/destination/live-state/:component_instance_id`
- `DELETE /events/:event_id/destination/live-state/:component_instance_id`
- `GET|POST /events/:event_id/destination/data-sources`
- `GET|PATCH|DELETE /events/:event_id/destination/data-sources/:id`
- `GET /public/events/:event_id/viewer`

Use the direct REST command for these operations and the main OpenAPI contract
for draft/component, adapter, and data-source payloads. A published destination
and a built custom app workspace are separate contracts.

### Optional custom event pages

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

Custom page endpoints require Director access. They are not prerequisites for
the default public event page or camera invitations.

### Live control

- `POST /events/:event_id/live/overlay`
- `POST /events/:event_id/live/leaderboard`
- `POST /events/:event_id/live/score`
- `POST /events/:event_id/live/notification`
- `POST /events/:event_id/live/featured_camera`
- `POST /events/:event_id/live/stats`

Featured camera uses `participant_identity` (`stream_<stream-id>`), or `null`
to clear. Overlay uses `action_type` (`show`, `update`, `hide`). Notifications,
overlays, leaderboard, score, and stats require a published custom event page;
featured camera selection also works on the default public page.

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

### Sponsor campaigns

Campaigns bind a sponsor to an event by `tag` — when a stream's `ad_tag`
matches an active campaign's tag, the viewer page renders the sponsor's
`banner_mobile` (portrait) or `banner_pillar` (immersive). The public skill
exposes these as "sponsors" via `bash scripts/streambridge sponsors ...`,
which is the natural word for organizers.

- `GET /events/:event_id/campaigns`
- `GET /events/:event_id/campaigns/:id`
- `POST /events/:event_id/campaigns` (multipart/form-data)
- `PATCH /events/:event_id/campaigns/:id` (multipart/form-data)
- `DELETE /events/:event_id/campaigns/:id`

Multipart fields (all optional on PATCH; `sponsor_name`, `tag`, and
`click_through_url` required on POST):

| Field | Type | Notes |
|---|---|---|
| `sponsor_name` | string | Display name shown on the viewer page |
| `campaign_name` | string | Internal label; can equal `sponsor_name` |
| `tag` | string | Matches `stream.ad_tag`. Slug: `a-z0-9_-`. Unique per active sponsor on the event. |
| `click_through_url` | string | https URL the banner links to |
| `alt_text` | string | Accessible alt text (≤240 chars). Defaults to `sponsor_name` if omitted. |
| `active` | boolean | `true` (default) or `false`; tag uniqueness only applies to active rows. |
| `logo` | file | ≤1 MB. png, jpg, webp, svg. |
| `banner_mobile` | file | ≤2 MB. png, jpg, webp. Wide aspect (~2.7:1), left-anchored. |
| `banner_pillar` | file | ≤5 MB. png, jpg, webp. Portrait, full-bleed. |

### Courses and the play world layer

The world layer is what an event's play world shows over its terrain: sponsor
placements, course points and hotspots. The CLI exposes it as
`bash scripts/streambridge courses ...` and `bash scripts/streambridge world ...`;
`WORLD.md` has the element rules.

- `GET /events/:event_id/routes`: courses with `world_status`, `world_error`, `world_built_at`, `world_url`
- `POST /events/:event_id/routes/:id/world/rebuild`: `202`; `409` when the course isn't parsed; `422` (`unavailable`) where worlds aren't built
- `GET /events/:event_id/world`: `{data: {version, elements}}`
- `PUT /events/:event_id/world`: body `{version, elements}`; replaces the layer; `?dry_run=true` checks without saving; `409` (`version_conflict`, with `current_version`) when the layer changed since `version`; `422` lists `elements[n].field` errors
- `POST /events/:event_id/world/elements`: one element
- `PATCH /events/:event_id/world/elements/:id`
- `DELETE /events/:event_id/world/elements/:id`
- `GET /public/events/:event_id/world`: the public layer (visible elements, active campaigns, public cameras)

### Athletes and trackers

An event's roster and the trackers that place athletes (and cameras that
aren't on the Stream app) on its map. A race is one of the event's courses.
Hosts only; reads need `events_read`, writes `events_write`.

- `GET /events/:event_id/athletes`: the roster by bib (`limit`, `offset`; `meta.total`), each with `trackers` and newest `location`
- `POST /events/:event_id/athletes`: one athlete: `name`, `bib`, `gender` (`female`/`male`, or `F`/`W`/`M`), `route_key` or `route_id`, `external_ref`, `hidden`, `tracker_ref` (+ `source_key` when there are several tracking sources)
- `POST /events/:event_id/athletes/batch`: body `{athletes: [rows]}`, at most 1,000; a row matches by `id`, then `bib`, then `external_ref`, else is added; each row is answered (`created`, `updated` or `error` with `errors`)
- `PATCH /events/:event_id/athletes/:id`, `DELETE /events/:event_id/athletes/:id`
- `PUT /events/:event_id/athletes/:id/photo`: multipart `photo` (png, jpg, webp, ≤5 MB); `DELETE` removes it
- `GET /events/:event_id/trackers`: `unassigned=true`, `source_key`, `limit`, `offset`
- `PATCH /events/:event_id/trackers/:id`: `{athlete_id}`, `{bib}` or `{stream_id}`; none of them unassigns
- `POST /events/:event_id/trackers/assign`: body `{assignments: [{tracker_id | tracker_ref (+ source_key), athlete_id | bib | stream_id}]}`; a `tracker_ref` that hasn't reported yet is registered
- Tracking sources are data sources: `POST /events/:event_id/destination/data-sources` with `adapter_key: "lnx"` answers a `webhook_url` for the provider; `GET …/data-sources/:id/webhook-deliveries` shows what it posted

### Public device and viewer endpoints

- `POST /public/events/:event_id/viewer_token`
- `GET /public/events/:event_id/sportraxs/races/:race_id/leaderboard`
- `GET /public/events/:event_id/sportraxs/races/:race_id/results`
- `GET /public/streams/by-key/:stream_key`
- `POST /public/streams/by-key/:stream_key/device-session`
- `GET /public/streams/by-key/:stream_key/livekit`
- `POST /public/streams/by-key/:stream_key/telemetry`
- `POST /public/streams/by-key/:stream_key/stream-metrics`

## Common payload examples

### Create an event

```bash
bash scripts/streambridge api POST /events '{"event":{"name":"Ridge Run"}}'
```

### Create an API token

```bash
bash scripts/streambridge auth tokens create "Codex laptop" 2026-12-31T23:59:59Z
```

### Create a stream

```bash
bash scripts/streambridge api POST /streams '{"stream":{"event_id":"<event-id>","name":"Finish Line","protocol":"srt"}}'
bash scripts/streambridge api PATCH /streams/<stream-id> '{"stream":{"publicly_visible":false}}'
```

Set `auto_start` **inside** the `stream` object. `false` creates a camera slot
without provisioning processing. The CLI sends it explicitly; `--start` changes
it to `true`. Current camera updates also accept `ad_tag`, `public_audio_enabled`,
`pinned_latitude`, and `pinned_longitude` (set both to null to clear).

Streams are public by default. Set `publicly_visible=false` to hide a camera
from public event pages while keeping invite URLs, device sessions, telemetry,
and publishing available.

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

## General operator MCP tools (`/mcp`)

The Rails compatibility transport exposes the tools below. The Node SDK transport
also has custom page, workspace, and live tools, uses `get_stream_invite` instead
of `get_stream_invite_url`, and does not expose `create_viewer_token`. Discover
the list from the endpoint you actually use. Direct REST covers viewer tokens.

The MCP tool set is narrower than the full REST API. When a route is not exposed as an MCP tool, use the bash CLI wrapper or direct REST fallback above.

- `list_events`
- `get_event`
- `create_event`
- `update_event`
- `delete_event`
- `list_streams`
- `get_stream`
- `create_stream`
- `update_stream_visibility`
- `start_stream`
- `stop_stream`
- `delete_stream`
- `get_stream_invite_url`
- `get_stream_metrics`
- `create_viewer_token`
- `get_event_world`
- `place_world_element`
- `update_world_element`
- `remove_world_element`
- `rebuild_course_world`
- `get_event_athletes`
- `upsert_athletes`
- `remove_athletes`
- `assign_trackers`
- `add_tracking_source`

The event tools (`list_events`, `get_event`, `update_event`, `create_viewer_token`), the
world tools and the athlete tools also reach the events the caller manages for another
organization; the camera tools stay with the caller's own organization.

## Host MCP tools (`/mcp/chatgpt`)

This dedicated profile uses resource-bound OAuth access tokens, organization
consent, and host scopes. It does not accept PATs or ordinary session JWTs.
Availability depends on pilot allowlisting and feature flags; reads and writes
are disabled by default. API deployment and a pilot grant are required before
these commands can work against production.

```bash
# Set STREAMBRIDGE_HOST_TOKEN securely to an already issued pilot OAuth grant.
bash scripts/streambridge mcp --profile host tools
bash scripts/streambridge mcp --profile host call get_workspace_context '{}'
bash scripts/streambridge mcp --profile host call get_event_workspace '{"event_id":"<event-id>"}'
```

| Tool | Purpose |
|---|---|
| `get_workspace_context` | Selected organization and capabilities |
| `list_events` | Search/page through events in that organization |
| `get_event_workspace` | Event, camera slots, programme and management links |
| `create_event` | Create a named event |
| `update_event_details` | Edit permitted event details with a revision |
| `add_camera` | Add a camera slot within the configured limit |
| `update_camera` | Edit camera details, visibility, audio or pin with a revision |
| `get_camera_invitation` | Open first-party camera invitation management |
| `get_event_readiness` | Timestamped setup, status and GPS evidence; media may be unknown |
| `prepare_live_show` | Prepare the optional programme, without starting processing |
| `open_obs_setup` | Open first-party OBS setup |

The table lists the 11 model-visible tools. Discovery also includes UI-only
`get_event_preview` (`ui.visibility=["app"]`), used by the embedded player for a
selected camera/live show. It needs `events_read streams_read`. Its `_meta` holds
a private, five-minute receive-only viewer session; do not invoke it as a text
workflow or copy that metadata into conversation/logs. Model-visible preview
output includes only IDs and expiry. Preview starts no capture or processing.

Read tool input schemas via `tools` rather than copying general REST payloads.
Mutations require a UUID `operation_id`; reuse the same ID and identical arguments
only when retrying that operation. Edits also require `expected_revision` from a
fresh read. On conflict, refresh and review before a new edit. The projection
returns no stream keys, encoder URLs, publishing/viewer tokens, or camera invite
secrets. Invitation and OBS setup return first-party handoffs. Check capabilities
before requesting writes; never infer verified video from setup/status alone.

MCP output is the JSON-RPC result object (tool failures include `isError`).
Requests negotiate the protocol and accept JSON or SSE. Both profiles exit
nonzero on HTTP, JSON-RPC, or `isError` tool failures. They do not retry writes.
`STREAMBRIDGE_MCP_URL` overrides the endpoint, independently of the REST base.

## Contract sources (monorepo)

- `docs/API_SPECIFICATION.md` and `docs/openapi/streambridge-v1.yaml`: general REST API
- `docs/openapi/chatgpt-host-v1.json`: generated host tool/API schemas
- `docs/features/chatgpt-host-mvp.md`: OAuth, gates and rollout limits

The bundled reference is an operations guide, not a duplicate of every schema.
Check the applicable contract before using an endpoint outside the named wrappers.
