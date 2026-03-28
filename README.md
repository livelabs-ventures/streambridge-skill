# StreamBridge Skill

Official StreamBridge skill for Claude Code, Codex, Manus, and other skills-compatible agents.

## Install

```bash
npx skills add https://github.com/livelabs-ventures/streambridge-skill --skill streambridge
```

## What is included

- `SKILL.md` with the operating instructions for agents
- `scripts/streambridge` bash CLI for StreamBridge API and MCP access
- `references/API.md` public API and MCP reference
- `references/COMMANDS.md` ready-to-run command examples
- `references/QUICKSTARTS.md` common starting prompts and flows
- `references/TROUBLESHOOTING.md` auth and runtime troubleshooting

## First run

From the root of the installed `streambridge` skill directory:

```bash
bash scripts/streambridge doctor
```

The CLI prompts for a personal access token on first use and stores it in `~/.streambridge/auth.json`.

## Public links

- Skill repo: `https://github.com/livelabs-ventures/streambridge-skill`
- Skill zip: `https://api.streambridge.live/downloads/streambridge-skill.zip`
- Product docs: `https://app.streambridge.live/docs/mcp`
