---
name: streambridge
description: Use StreamBridge from Claude Code, Codex, Manus, and other skills-compatible agents. Use it for events, cameras, invite links, viewer tokens, pages, live controls, sponsors, the play world layer (sponsor placements, course points and hotspots in an event's 3D world), feedback, and direct API or MCP access.
license: Proprietary
---

# StreamBridge

Use this skill when the user wants to create or run a StreamBridge event from an agent instead of the web UI.

## Default approach

For a PAT-backed operator workflow, prefer the bundled Bash CLI in `scripts/streambridge`. Use the Python quickstart when one-shot setup is useful. For a scoped ChatGPT workflow, use the host MCP profile and its first-party invitation/OBS handoffs; keep its capability and credential boundaries.

## Requirements

Requires bash and curl for REST, Python 3.10+ for MCP or helpers, and network access. jq is optional except for sponsor name resolution and import.

## Setup

For general operator REST/MCP, verify auth before substantial work. The host
profile instead requires its own issued OAuth grant and capability checks.

1. If no saved token exists yet, the CLI asks for a StreamBridge API token on first run.
2. The token is stored locally in `~/.streambridge/auth.json`.
3. Run `bash scripts/streambridge doctor` if auth or connectivity is unclear.

## Golden path

StreamBridge hosts endurance sports. For a new event:

1. Create a named event. Its public map, featured stream, and chat page exists at `/v/<event-id>` immediately.
2. Add camera slots (public by default) and retrieve invitations for the intended operators.
3. Return the watch link and management link. Confirm actual media and current telemetry before claiming a camera is live.
4. If the host requests an OBS show, prepare the optional programme with `events prepare-live-show <event-id>` and hand off to the event's OBS setup. Preparation does not start processing.

Camera creation defaults to `auto_start=false`. Connect the phone or encoder to begin sending video; use `--start` only when processing startup is explicitly needed. A database status or successful setup command does not prove visible video.

One-shot setup:

```bash
python3 scripts/quickstart.py "Ridge Run" --camera-name "Start" --camera-name "Finish"
```

This returns camera invitations and public watch/manage URLs without starting processing or building a custom page. Set `STREAMBRIDGE_APP_URL` for a non-production frontend. If setup fails, use the returned partial resource IDs to finish the existing event instead of rerunning creation.

## MCP profiles

- `mcp tools` / `mcp call ...`: general operator tools at `/mcp`, using the saved PAT or `STREAMBRIDGE_API_TOKEN`. Responses can contain credentials.
- `mcp --profile host tools` / `mcp --profile host call ...`: the 11 model-visible scoped host tools at `/mcp/chatgpt`, using **only** `STREAMBRIDGE_HOST_TOKEN`, an OAuth access token bound to that resource and one organization. A PAT cannot authorize this profile.

The host profile is a gated pilot, with reads/writes disabled by default. ChatGPT uses account linking; the CLI's token override is for testing an issued grant. Do not request a PAT for ChatGPT account linking or imply the pilot is publicly available. Follow `references/API.md` for tool names, operation IDs, revisions, capabilities, and first-party handoffs.

The host profile also includes a native ChatGPT sidebar app and conversation
panel. `get_workspace_context` opens Event workspace; event/camera tools return
the same safe data with a UI resource. Use the panel for event creation, camera
editing and readiness, or use the same tools conversationally. The CLI remains
text-only. Discovery also lists the UI-only `get_event_preview`; leave it to the
embedded player and never copy its private `_meta` viewer credential into model
context or logs. The panel previews one already-publishing source, muted by
default, with no capture or stream-control permission. Invitation credentials and OBS setup still use protected first-party
links. `embedded_ui=true` does not imply remote capture or verified video.

## Preferred commands

- Health and auth verification: `bash scripts/streambridge doctor`
- Events: `bash scripts/streambridge events ...`
- Cameras and streams: `bash scripts/streambridge streams ...`
  - Cameras are public by default; use `streams update <stream-id> --hidden`
    or `--public` to control public event page visibility.
- Optional custom pages and builds: `bash scripts/streambridge page ...`
- Live overlays and switching: `bash scripts/streambridge live ...`
- Feedback: `bash scripts/streambridge feedback ...`
- Sponsors (logos and banners on the viewer page): `bash scripts/streambridge sponsors ...`
- Courses and their play worlds: `bash scripts/streambridge courses ...`
- The play world layer (sponsor placements, course points, hotspots): `bash scripts/streambridge world ...`
- Direct REST fallback: `bash scripts/streambridge api <METHOD> <PATH> '<json>'`
- Direct MCP fallback: `bash scripts/streambridge mcp call <tool> '<json>'`

## Managing sponsors

Sponsors are bound to a camera via an `ad_tag`. When a viewer watches that
camera, the public page renders the sponsor's mobile banner (portrait) or
pillar banner (landscape immersive) and routes click-throughs to the
sponsor's URL.

Every sponsor verb accepts either a sponsor name OR a sponsor id — resolve
the organizer's natural reference ("the Cell C sponsor", "update Toyota's
pillar to ...") to the right call without asking them for a uuid.

Common operations:

- Show what's configured: `bash scripts/streambridge sponsors list <event-id>`
- Inspect one: `bash scripts/streambridge sponsors show <event-id> "Cell C"`
- Add a new sponsor (all-in-one):

  ```bash
  bash scripts/streambridge sponsors add <event-id> "Cell C" \
    --on start_line \
    --link https://cellc.co.za/comrades \
    --logo logo.svg --mobile mobile.png --pillar pillar.png
  ```

- Update any field, including swapping an asset:

  ```bash
  bash scripts/streambridge sponsors set <event-id> "Cell C" --logo new-logo.svg
  bash scripts/streambridge sponsors set <event-id> "Cell C" --link https://...
  ```

- Asset-only swap (more honest verb when only changing artwork):

  ```bash
  bash scripts/streambridge sponsors replace-asset <event-id> "Toyota" --pillar new-pillar.png
  ```

- Temporarily hide / show again: `pause` / `resume`
- Remove: `bash scripts/streambridge sponsors remove <event-id> "Cell C"`
- Bulk import from a manifest: `bash scripts/streambridge sponsors import <event-id> sponsors.json`

Asset rules to respect when uploading:

| Asset | Max size | MIME types | When used |
|---|---|---|---|
| `--logo` | 1 MB | png, jpg, webp, svg | Small mark composited on the map marker pill |
| `--mobile` | 2 MB | png, jpg, webp | Full-width banner on phones (~2.7:1, design with logo/copy left-anchored) |
| `--pillar` | 5 MB | png, jpg, webp | Portrait, full-bleed immersive on the desktop watch page |

Important: tags must be unique among **active** sponsors per event. To
re-use an `ad_tag`, `pause` or `remove` the previous sponsor first.

## The play world layer

An event's course is shown as a 3D play world on its public page. The server builds the terrain; you place things in it: sponsor placements (a campaign's logo at a kilometre), course points (aid, water, cut-offs, climbs, landmarks) and hotspots that open a camera or a link. Viewers see changes live.

Read `references/WORLD.md` before editing a layer. The loop:

```bash
bash scripts/streambridge courses list <event-id>              # course keys, distances, world status
bash scripts/streambridge sponsors list <event-id>             # campaigns to place
bash scripts/streambridge world pull <event-id> world.json
# edit world.json
bash scripts/streambridge world check <event-id> world.json
bash scripts/streambridge world push <event-id> world.json
```

Anchor to a course and kilometre whenever you can. Report what you placed (kind, label, course and km) and any course whose world isn't `ready` (its elements won't show until it is).

## Optional custom pages

The default public event page needs no workspace build or publish call. The `page` commands manage the advanced custom page workspace, which requires Director access. Use it only when requested.

`quickstart.py --custom-page` builds a custom preview. `--publish` explicitly builds and publishes that custom page; the compatibility flag `--no-publish` builds a preview only. Respect the user's existing publication authorization. Do not restart quickstart to publish an existing event; use `page publish <event-id>`.

## Output expectations

When reporting back, include:

- event name and id
- camera names
- operator CLI: invitation links for intended camera operators; host MCP: protected invitation/OBS management handoffs
- public watch and management URLs; custom preview/published URL if requested
- blockers preventing live readiness

## Troubleshooting

If the CLI fails:

1. read the exact API error
2. run `bash scripts/streambridge doctor` if auth or API reachability may be involved
3. prefer fixing the CLI path over falling back to the UI
4. if a wrapper is missing, use `references/API.md` and the direct endpoint allowed by the existing grant
5. use the first-party invitation/OBS handoff when the host profile returns one; this is its intended flow
6. do not substitute a PAT or broader operator tools to bypass a host capability denial

## Gotchas

- Prefer the bash CLI over the Python helpers for repeatable operations.
- Use `references/API.md` when the CLI wrapper does not cover the exact endpoint.
- Inspect the tool list in the intended MCP profile before assuming a tool exists.
- REST base overrides: `STREAMBRIDGE_API_BASE` (preferred), `STREAMBRIDGE_API_BASE_URL`, or `STREAMBRIDGE_API_URL`; either origin or `/api/v1` URL is accepted. `STREAMBRIDGE_MCP_URL` overrides the selected profile endpoint.
- The public GitHub skill and downloadable zip follow main publication and API deployment; a branch update is source verification only.

## References

- `references/API.md`
- `references/COMMANDS.md`
- `references/QUICKSTARTS.md`
- `references/TROUBLESHOOTING.md`
- `references/WORLD.md`
