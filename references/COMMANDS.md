# StreamBridge Skill Commands

Run these commands from the root of the installed `streambridge` skill directory. Prefer the bash CLI first.

On first run, the skill asks for your token and stores it in `~/.streambridge/auth.json`.

## Health check

```bash
bash scripts/streambridge doctor
```

## Common operations

```bash
bash scripts/streambridge events create "School Rugby Finals"
bash scripts/streambridge streams create <event-id> "Touchline"
bash scripts/streambridge streams invite <stream-id>
bash scripts/streambridge page init <event-id> --prompt "Create a clean sports page"
bash scripts/streambridge page files-list <event-id>
bash scripts/streambridge page build <event-id>
bash scripts/streambridge page preview <event-id>
bash scripts/streambridge page publish <event-id>
```

## Auth tokens

```bash
bash scripts/streambridge auth tokens list
bash scripts/streambridge auth tokens create "Codex laptop"
bash scripts/streambridge auth tokens delete <token-id>
```

## Organizations

```bash
bash scripts/streambridge organizations list --query streambridge
bash scripts/streambridge organizations show <organization-id>
bash scripts/streambridge organizations switch <organization-id>
```

## Event

```bash
bash scripts/streambridge events create "Cape Epic"
bash scripts/streambridge events list
bash scripts/streambridge events show <event-id>
bash scripts/streambridge events update <event-id> "Cape Epic Day 2"
bash scripts/streambridge events delete <event-id>
```

## Camera and stream

```bash
bash scripts/streambridge streams list --event-id <event-id>
bash scripts/streambridge streams create <event-id> "Finish Line"
bash scripts/streambridge streams update <stream-id> --name "Finish Line A" --protocol srt
bash scripts/streambridge streams show <stream-id>
bash scripts/streambridge streams start <stream-id>
bash scripts/streambridge streams stop <stream-id>
bash scripts/streambridge streams invite <stream-id>
bash scripts/streambridge streams metrics <stream-id> --limit 50
```

## Page

```bash
bash scripts/streambridge page init <event-id> --prompt "Create a simple sports page"
bash scripts/streambridge page status <event-id>
bash scripts/streambridge page update <event-id> --prompt "Refine the sports layout"
bash scripts/streambridge page files-list <event-id> --path src/components
bash scripts/streambridge page file-read <event-id> src/App.tsx
bash scripts/streambridge page file-write <event-id> src/data.json '{"title":"Final"}'
bash scripts/streambridge page file-replace <event-id> src/App.tsx "Old text" "New text" --all
bash scripts/streambridge page build <event-id>
bash scripts/streambridge page preview <event-id>
bash scripts/streambridge page render <event-id>
bash scripts/streambridge page live-url <event-id>
bash scripts/streambridge page publish <event-id>
bash scripts/streambridge page versions <event-id>
bash scripts/streambridge page rollback <event-id> 2
```

## Live

```bash
bash scripts/streambridge live switch-camera <event-id> stream_<stream-id>
bash scripts/streambridge live notification <event-id> "Live now" --message "We are ready to go live"
bash scripts/streambridge live overlay <event-id> lower-third show "Semi Final" --position top-left --duration-ms 3000 --animate true
bash scripts/streambridge live leaderboard <event-id> '[{"position":1,"athlete_name":"A. Runner"}]' --label "Overall" --tab-index 0
bash scripts/streambridge live stats <event-id> '[{"label":"Possession","value":"62%"}]' "Match stats"
```

## Feedback

```bash
bash scripts/streambridge feedback list --status open
bash scripts/streambridge feedback roadmap
bash scripts/streambridge feedback create --title "Lower-third editor" --description "Need reusable lower-thirds." --kind feature_request
bash scripts/streambridge feedback update <feedback-id> --title "Lower-third editor v2"
bash scripts/streambridge feedback comments <feedback-id>
bash scripts/streambridge feedback comment <feedback-id> "This is needed before the next event."
bash scripts/streambridge feedback vote <feedback-id>
bash scripts/streambridge feedback unvote <feedback-id>
bash scripts/streambridge feedback follow <feedback-id>
bash scripts/streambridge feedback unfollow <feedback-id>
bash scripts/streambridge feedback status <feedback-id> planned "Queued for the next release"
bash scripts/streambridge feedback priority <feedback-id> high
bash scripts/streambridge feedback duplicate <feedback-id> <canonical-feedback-id> "Tracked elsewhere"
```

## Sponsors

```bash
# Show what's configured on this event
bash scripts/streambridge sponsors list <event-id>

# Show one sponsor (resolve by name OR id)
bash scripts/streambridge sponsors show <event-id> "Cell C"

# Add a sponsor with all three assets
bash scripts/streambridge sponsors add <event-id> "Cell C" \
  --on start_line \
  --link https://cellc.co.za/comrades \
  --logo ./cellc/logo.svg \
  --mobile ./cellc/mobile.png \
  --pillar ./cellc/pillar.png

# Add a sponsor with no assets yet (logo + banners added later)
bash scripts/streambridge sponsors add <event-id> "Toyota" \
  --on lead_car --link https://toyota.co.za

# Swap one asset (by sponsor name)
bash scripts/streambridge sponsors replace-asset <event-id> "Toyota" \
  --pillar ./toyota/pillar-v2.png

# Update any other field
bash scripts/streambridge sponsors set <event-id> "Cell C" --link https://new-url.example
bash scripts/streambridge sponsors set <event-id> "Cell C" --on women_lead --logo ./cellc/v2.svg

# Pause / resume
bash scripts/streambridge sponsors pause  <event-id> "Cell C"
bash scripts/streambridge sponsors resume <event-id> "Cell C"

# Remove
bash scripts/streambridge sponsors remove <event-id> "Cell C"

# Bulk from a manifest. Relative asset paths resolve against the manifest's directory.
bash scripts/streambridge sponsors import <event-id> ./sponsors.json
```

Manifest shape (`sponsors.json`):

```json
{
  "sponsors": [
    {
      "name": "Cell C",
      "on": "start_line",
      "link": "https://cellc.co.za/comrades",
      "alt": "Cell C × Comrades — Buy Comrades Bundles",
      "logo": "./cellc/logo.svg",
      "mobile": "./cellc/mobile.png",
      "pillar": "./cellc/pillar.png",
      "active": true
    }
  ]
}
```

## Public device and viewer flows

```bash
bash scripts/streambridge public viewer-token <event-id> "Viewer Name"
bash scripts/streambridge public stream <stream-key>
bash scripts/streambridge public device-session <stream-key> <device-id>
bash scripts/streambridge public livekit <stream-key> --device-token <device-token>
bash scripts/streambridge public telemetry <stream-key> -33.92 18.42 --device-token <device-token>
bash scripts/streambridge public stream-metrics <stream-key> 4200 120 3 --packet-loss 0.2 --device-token <device-token>
```

## Direct API and MCP fallback

```bash
bash scripts/streambridge api GET /organizations
bash scripts/streambridge api POST /events '{"event":{"name":"School Rugby Finals"}}'
bash scripts/streambridge mcp tools
bash scripts/streambridge mcp call create_viewer_token '{"event_id":"<event-id>","viewer_name":"Viewer"}'
```

## Optional helper

If you explicitly want the one-shot scaffold helper, keep using:

```bash
python3 scripts/quickstart.py "Create a school rugby event with three cameras and a simple live page"
```
