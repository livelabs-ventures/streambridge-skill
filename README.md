# StreamBridge Skill

This directory is the canonical source for the public `streambridge` skill.

## Repository model

- Source of truth: the monorepo at `services/streambridge/skills/streambridge`
- Public mirror: `https://github.com/livelabs-ventures/streambridge-skill`
- Publish mechanism: `git subtree split`

The public repo is a publish target, not a second source of truth.

## Local commands

Run commands from the root of the installed skill directory:

```bash
python3 scripts/doctor.py
python3 scripts/quickstart.py "Create a school rugby event with touchline, scoreboard, and crowd cameras"
```

## Publishing the public repo

From the monorepo root:

```bash
scripts/publish-streambridge-skill-subtree.sh
```

Environment overrides:

- `PUBLIC_SKILL_REMOTE_NAME`
- `PUBLIC_SKILL_REMOTE_URL`
- `PUBLIC_SKILL_SPLIT_BRANCH`
- `PUBLIC_SKILL_TARGET_BRANCH`
