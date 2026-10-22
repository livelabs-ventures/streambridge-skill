# StreamBridge Skill Quickstarts

Run from the installed skill directory. First use prompts for a PAT.

## Endurance event

```bash
python3 scripts/quickstart.py "Ridge Run" --camera-name "Start" --camera-name "Finish"
```

Creates a public event and two camera slots, retrieves authenticated invitations,
and returns watch/manage URLs. It does not start processing or build a custom
page. Connect the cameras, then inspect media and telemetry in StreamBridge.
For a non-production app set `STREAMBRIDGE_APP_URL` to its frontend origin.

For separate commands:

```bash
bash scripts/streambridge events create "Ridge Run"
bash scripts/streambridge streams create <event-id> "Start"
bash scripts/streambridge streams create <event-id> "Finish"
bash scripts/streambridge streams invite <stream-id>
```

The default viewer is `https://app.streambridge.live/v/<event-id>`.
Management is `https://app.streambridge.live/events/<event-id>`.

## Athletes on the map

```bash
bash scripts/streambridge courses list <event-id>                   # race keys
bash scripts/streambridge athletes connect <event-id> lnx           # give LNX the webhook URL
bash scripts/streambridge athletes import <event-id> roster.json    # name, bib, gender, route_key, tracker_ref
bash scripts/streambridge athletes list <event-id>
```

The roster shows on the public page at once. An athlete appears on the map only
once their tracker reports a position (`location` in `athletes list`).

## Optional OBS show

```bash
bash scripts/streambridge events prepare-live-show <event-id>
```

Idempotently prepares a programme, without starting processing. Open the event's
OBS setup to configure the camera inputs and show output. A programme is separate
from the source cameras and cannot receive a camera invitation.

## Optional custom page (Director)

```bash
python3 scripts/quickstart.py "Ridge Run" --custom-page
```

Creates a new event, builds its custom page and returns a preview. Pass `--publish`
only when publication is authorized. To publish an existing preview, use
`bash scripts/streambridge page publish <event-id>`; do not rerun quickstart.
The compatibility `--no-publish` flag also selects a custom preview.

## ChatGPT pilot

Use account linking for the host profile. The CLI can inspect an already issued
pilot grant in `STREAMBRIDGE_HOST_TOKEN`:

```bash
bash scripts/streambridge mcp --profile host tools
bash scripts/streambridge mcp --profile host call get_workspace_context '{}'
```

The feature is gated and disabled by default. PATs authorize the general operator
CLI only. See `API.md` for the host schemas and first-party handoffs.
