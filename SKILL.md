---
name: streambridge
description: Use StreamBridge from Claude Code, Codex, Manus, and other skills-compatible agents. Use it for events, cameras, invite links, viewer tokens, pages, live controls, feedback, and direct API or MCP access.
license: Proprietary
compatibility: Designed for skills-compatible agents. Requires bash, curl, and network access to StreamBridge. jq is optional for prettier JSON output.
---

# StreamBridge

Use this skill when the user wants to create or run a StreamBridge event from an agent instead of the web UI.

## Default approach

Prefer the bundled bash CLI in `scripts/streambridge` for real actions. Use the older Python helpers only when the one-shot scaffold is genuinely faster for the task.

## Setup

Before substantial work:

1. If no saved token exists yet, the CLI asks for a StreamBridge API token on first run.
2. The token is stored locally in `~/.streambridge/auth.json`.
3. Run `bash scripts/streambridge doctor` if auth or connectivity is unclear.

## Golden path

For a new event, prefer:

1. Create the event and cameras with `bash scripts/streambridge ...` commands.
2. Review the event, cameras, invite links, and preview URL
3. Ask whether to publish unless the user explicitly requested publish
4. If approved, run `bash scripts/streambridge page publish <event-id>`

If the user explicitly wants a one-shot scaffold, the optional helper is:

```bash
python3 scripts/quickstart.py "<user intent>" --template <template>
```

## Preferred commands

- Health and auth verification: `bash scripts/streambridge doctor`
- Events: `bash scripts/streambridge events ...`
- Cameras and streams: `bash scripts/streambridge streams ...`
- Event pages and builds: `bash scripts/streambridge page ...`
- Live overlays and switching: `bash scripts/streambridge live ...`
- Feedback: `bash scripts/streambridge feedback ...`
- Direct REST fallback: `bash scripts/streambridge api <METHOD> <PATH> '<json>'`
- Direct MCP fallback: `bash scripts/streambridge mcp call <tool> '<json>'`

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

If the CLI fails:

1. read the exact API error
2. run `bash scripts/streambridge doctor` if auth or API reachability may be involved
3. prefer fixing the CLI path over falling back to the UI
4. if the wrapper command does not exist yet, use `references/API.md` and call the REST or MCP endpoint directly
5. only switch to manual UI steps if the CLI and direct API/MCP path are both genuinely blocked

## Gotchas

- Prefer the bash CLI over the Python helpers for repeatable operations.
- Use `references/API.md` when the CLI wrapper does not cover the exact endpoint.
- Use `bash scripts/streambridge mcp tools` to inspect the live MCP tool list before assuming a tool exists.

## References

- `references/API.md`
- `references/COMMANDS.md`
- `references/QUICKSTARTS.md`
- `references/TROUBLESHOOTING.md`
