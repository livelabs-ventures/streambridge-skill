# StreamBridge Skill Troubleshooting

## `Unauthorized`

- Confirm the token you entered is valid
- Confirm the token starts with `sb_pat_`
- Run `python3 skills/streambridge/scripts/doctor.py`

## API connection failed

- Run `python3 skills/streambridge/scripts/doctor.py`
- Check `STREAMBRIDGE_API_BASE_URL` if you are not targeting production
- Remove `~/.streambridge/auth.json` and rerun if you need to re-enter the token

## Publish failed

- Check `python3 skills/streambridge/scripts/page.py status <event-id>`
- Ensure the page has been built successfully first

## Camera failed to start

- Inspect the stream with `python3 skills/streambridge/scripts/camera.py show <stream-id>`
- Retry the start command

## Quickstart stopped before publish

- That is the expected default behavior
- Publish explicitly with `python3 skills/streambridge/scripts/page.py publish <event-id>`
- Or rerun quickstart with `--publish`
