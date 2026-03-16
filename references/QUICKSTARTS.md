# StreamBridge Skill Quickstarts

Run these after installing the skill. If you have not used it before, it will ask for your API token first.

## Grassroots sports

```bash
python3 skills/streambridge/scripts/quickstart.py "Create a school rugby event with touchline, scoreboard, and crowd cameras"
```

Expected outcome:

- event created
- cameras created and started
- invite links returned
- preview URL returned
- publish confirmation still under operator control

## Endurance race

```bash
python3 skills/streambridge/scripts/quickstart.py "Create an ultra-trail event with start, checkpoint, and finish cameras plus a race page" --template race
```

Expected outcome:

- race-oriented event page prepared
- camera invites returned
- page preview available

## Breaking news

```bash
python3 skills/streambridge/scripts/quickstart.py "Breaking: factory fire in Lyon. Create a live event with three field cameras and prepare to publish" --template news
```

Expected outcome:

- rapid event setup
- field camera invites returned
- preview or publish-ready state reached quickly
