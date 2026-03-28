# StreamBridge Skill Troubleshooting

## `Unauthorized`

- Confirm the token you entered is valid
- Confirm the token starts with `sb_pat_`
- Run `bash scripts/streambridge doctor`

## API connection failed

- Run `bash scripts/streambridge doctor`
- Check `STREAMBRIDGE_API_BASE` or `STREAMBRIDGE_API_URL` if you are not targeting production
- Remove `~/.streambridge/auth.json` and rerun if you need to re-enter the token

## Publish failed

- Check `bash scripts/streambridge page status <event-id>`
- Ensure the page has been built successfully first

## Device-authenticated public commands failed

- Create a fresh device session with `bash scripts/streambridge public device-session <stream-key> <device-id>`
- Pass the returned device token with `--device-token ...` or set `STREAMBRIDGE_DEVICE_TOKEN`
- Retry `bash scripts/streambridge public livekit ...`, `telemetry ...`, or `stream-metrics ...`

## Camera failed to start

- Inspect the stream with `bash scripts/streambridge streams show <stream-id>`
- Retry the start command

## CLI wrapper does not cover the operation

- Use `references/API.md`
- Call the REST endpoint with `bash scripts/streambridge api ...`
- Or call MCP directly with `bash scripts/streambridge mcp ...`

## One-shot helper stopped before publish

- That is the expected default behavior
- Publish explicitly with `bash scripts/streambridge page publish <event-id>`
- Or rerun the helper with `--publish`
