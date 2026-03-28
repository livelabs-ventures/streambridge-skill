# StreamBridge Skill Quickstarts

Run these after installing the skill. If you have not used it before, it will ask for your API token first.

## Grassroots sports

```bash
bash scripts/streambridge events create "School Rugby Event"
bash scripts/streambridge streams create <event-id> "Touchline" --start
bash scripts/streambridge streams create <event-id> "Scoreboard" --start
bash scripts/streambridge streams create <event-id> "Crowd" --start
bash scripts/streambridge page init <event-id> --prompt "Create a school rugby event page with touchline, scoreboard, and crowd cameras"
```

Expected outcome:

- event created
- cameras created and started
- invite links returned
- preview URL returned
- publish confirmation still under operator control

## Endurance race

```bash
bash scripts/streambridge events create "Ultra Trail"
bash scripts/streambridge streams create <event-id> "Start" --start
bash scripts/streambridge streams create <event-id> "Checkpoint" --start
bash scripts/streambridge streams create <event-id> "Finish" --start
bash scripts/streambridge page init <event-id> --prompt "Create a race page with start, checkpoint, finish, stats, and leaderboard sections" --starter-kit race
```

Expected outcome:

- race-oriented event page prepared
- camera invites returned
- page preview available

## Breaking news

```bash
bash scripts/streambridge events create "Breaking News"
bash scripts/streambridge streams create <event-id> "Field Camera 1" --start
bash scripts/streambridge streams create <event-id> "Field Camera 2" --start
bash scripts/streambridge page init <event-id> --prompt "Create a breaking news page with two field cameras and fast-switch layout" --starter-kit news
```

Expected outcome:

- rapid event setup
- field camera invites returned
- preview or publish-ready state reached quickly

## One-shot helper

If a single scaffold command is genuinely better for the task, the optional helper remains available:

```bash
python3 scripts/quickstart.py "Create a breaking news event with three field cameras and prepare to publish" --template news
```
