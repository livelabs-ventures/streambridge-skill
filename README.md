# StreamBridge Skill

Official StreamBridge skill for Claude Code, Codex, Manus, and other skills-compatible agents.

## Install

```bash
npx skills add https://github.com/livelabs-ventures/streambridge-skill --skill streambridge
```

## What is included

- `SKILL.md` with the operating instructions for agents
- `scripts/streambridge` bash CLI for REST and general/host MCP profiles
- `scripts/mcp.py` stdlib Streamable HTTP client with JSON/SSE support
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

REST commands require Bash and curl. MCP and Python helpers require Python 3.10+.
`jq` is optional for JSON display, but required for sponsor name lookup/import and athlete bib lookup/import.
The default flow creates a public endurance event and camera slots; custom page
build/publish and processing startup are explicit options. See the references.
The host MCP pilot uses resource-bound OAuth, not the normal PAT, and is disabled
by default. Source support does not imply public pilot availability.

## Public links

- Skill repo: `https://github.com/livelabs-ventures/streambridge-skill`
- Skill zip: `https://api.streambridge.live/downloads/streambridge-skill.zip`
- Product docs: `https://app.streambridge.live/docs/mcp`

## Where this lives in the monorepo (for maintainers)

This directory — `services/streambridge/skills/streambridge/` — is **the single source of truth** for the public skill. There is no separate clone of the public repo checked in; the public repo is a **generated artifact** produced from this prefix.

Two consumers read from this exact path:

- `scripts/publish-streambridge-skill-subtree.sh` runs `git subtree split --prefix=services/streambridge/skills/streambridge` and pushes the resulting branch to `public-skill main` (`github.com/livelabs-ventures/streambridge-skill`).
- `services/streambridge/app/controllers/docs_controller.rb#build_skill_archive` walks this directory at request time to assemble the `/downloads/streambridge-skill.zip` archive.

## Release flow

1. Edit files **here** (in `services/streambridge/skills/streambridge/`). Never edit anything inside the public repo directly — it'll get overwritten on the next subtree push.
2. Commit changes to the monorepo on a normal feature branch and merge to `main`.
3. `.github/workflows/publish-streambridge-skill.yml` publishes the subtree on main changes. For an authorized manual release from merged main, run:

   ```bash
   bash scripts/publish-streambridge-skill-subtree.sh
   ```

   The script is idempotent. It splits the current commit's subtree and force-pushes to `public-skill main`. If `public-skill` isn't registered as a remote, it adds it (URL: `git@github.com:livelabs-ventures/streambridge-skill.git`).

4. The Rails-served zip at `/downloads/streambridge-skill.zip` updates **automatically** on the next API deploy — it reads from the same files at request time, no rebuild step required.

## Validation before release

From the monorepo root:

```bash
bash -n services/streambridge/skills/streambridge/scripts/streambridge
python3 -m unittest discover -s scripts/tests -p 'test_streambridge_*.py'
cd tools/mcp-server && npm test && npm run contract:check
```

The CLI tests use a local HTTP fixture; MCP tests exercise both profiles against
the actual SDK server. They do not prove deployed API, camera video, OBS or
ChatGPT account linking. A draft branch does not update either public artifact.

## Why this structure

The public skill needs its own GitHub repo for `npx skills add` URLs to work cleanly, but maintaining two parallel checkouts (or a submodule) drifts within weeks. Subtree split keeps the monorepo as the operational source of truth, lets the public repo carry only the user-facing slice, and makes "did we forget to publish" answerable by `git log` on this directory.
