---
name: streambridge
description: Use StreamBridge from Claude Code, Codex, Manus, and other skills-compatible agents. This skill is the product: it bundles its own scripts for event setup, camera invites, page lifecycle, and live control.
---

# StreamBridge

Use this skill when the user wants to create or run a StreamBridge event from an agent instead of the web UI.

## Default approach

Prefer the bundled scripts in `scripts/` for real actions. Do not require a separate CLI for the core workflow.

## Setup

Before substantial work:

1. If no saved token exists yet, the scripts will ask for a StreamBridge API token on first run.
2. The token is stored locally in `~/.streambridge/auth.json`.
3. Run `python3 scripts/doctor.py` if auth or connectivity is unclear.

## Golden path

For a new event, prefer:

1. Run `python3 scripts/quickstart.py "<user intent>" --template <template>`
2. Review the event, cameras, invite links, and preview URL
3. Ask whether to publish unless the user explicitly requested publish
4. If approved, run `python3 scripts/page.py publish <event-id>`

## Script selection

- New event setup: `scripts/quickstart.py`
- Event operations: `scripts/event.py`
- Camera setup and invites: `scripts/camera.py`
- Event page lifecycle: `scripts/page.py`
- Live operations: `scripts/live.py`
- Health and auth verification: `scripts/doctor.py`

## Publish rule

Do not publish by default during setup unless:

- the user explicitly asked to publish, or
- the script call includes `--publish`

If setup reaches a ready state without publish, show the preview URL and ask whether to publish.

## Output expectations

When reporting back, include:

- event name and id
- camera names
- invite links or QR-ready URLs
- preview URL or published URL
- blockers preventing live readiness

## Troubleshooting

If a script fails:

1. read the exact API error
2. run `scripts/doctor.py` if auth or API reachability may be involved
3. prefer fixing the scripted path over falling back to the UI
4. only switch to MCP or manual UI steps if the scripted path is genuinely blocked

## References

- `references/COMMANDS.md`
- `references/QUICKSTARTS.md`
- `references/TROUBLESHOOTING.md`
