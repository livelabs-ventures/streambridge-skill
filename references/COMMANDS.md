# StreamBridge Skill Commands

The StreamBridge skill ships with bundled Python scripts under `skills/streambridge/scripts/`.

On first run, the skill asks for your token and stores it in `~/.streambridge/auth.json`.

## Health check

```bash
python3 skills/streambridge/scripts/doctor.py
```

## Quickstart

```bash
python3 skills/streambridge/scripts/quickstart.py "Create a school rugby event with three cameras and a simple live page"
python3 skills/streambridge/scripts/quickstart.py "Create a breaking news event with three field cameras" --template news --publish
```

## Event

```bash
python3 skills/streambridge/scripts/event.py create --name "Cape Epic"
python3 skills/streambridge/scripts/event.py list
python3 skills/streambridge/scripts/event.py show <event-id>
```

## Camera

```bash
python3 skills/streambridge/scripts/camera.py add <event-id> --name "Finish Line"
python3 skills/streambridge/scripts/camera.py list <event-id>
python3 skills/streambridge/scripts/camera.py show <stream-id>
python3 skills/streambridge/scripts/camera.py start <stream-id>
python3 skills/streambridge/scripts/camera.py stop <stream-id>
python3 skills/streambridge/scripts/camera.py invite <stream-id>
```

## Page

```bash
python3 skills/streambridge/scripts/page.py init <event-id> --prompt "Create a simple sports page"
python3 skills/streambridge/scripts/page.py status <event-id>
python3 skills/streambridge/scripts/page.py build <event-id>
python3 skills/streambridge/scripts/page.py preview <event-id>
python3 skills/streambridge/scripts/page.py publish <event-id>
python3 skills/streambridge/scripts/page.py versions <event-id>
```

## Live

```bash
python3 skills/streambridge/scripts/live.py switch-camera <event-id> --camera <identity>
python3 skills/streambridge/scripts/live.py notification <event-id> --title "Live now" --message "We are ready to go live"
```

## Optional CLI

If you prefer a shell-first workflow, the standalone `streambridge` CLI can wrap the same API flows later. The skill does not require it.
