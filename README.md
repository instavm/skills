# InstaVM Skills

Agent skill set for [InstaVM](https://instavm.io), following the [Agent Skills](https://agentskills.io) format.

## Installation

Install with the `skills` CLI:

```bash
npx skills add instavm/skills
```

Supports Codex, Claude Code, Cursor, OpenCode, and other agents supported by `skills`.

## Claude Code Plugin Marketplace

Add the marketplace:

```text
/plugin marketplace add instavm/skills
```

Install the plugin:

```text
/plugin install instavm@instavm-skills
```

## Skill Surface

This repo currently ships one installable skill:

- [`use-instavm`](plugins/instavm/skills/use-instavm/SKILL.md)

`use-instavm` is route-first. Intent routing is defined in `SKILL.md`, and execution details are split into action-oriented references. It uses the installed `instavm` CLI for quick operator workflows, the Python SDK for orchestration-heavy tasks, and raw HTTP only for confirmed gaps.

## Workflow Coverage

`use-instavm` covers:

- ephemeral code execution sessions
- durable VM lifecycle operations
- static site and small app hosting
- VM snapshots and clones
- OCI-image snapshot builds
- SSH key registration and SSH access
- share creation for exposed ports
- session and VM egress policy management
- volume creation, upload, checkpoint, mount, and unmount
- installed CLI auth, identity, docs, billing, and operator workflows
- platform APIs such as computer-use, audit, webhooks, and API keys

## Repository Structure

```text
skills/
├── .claude-plugin/
│   └── marketplace.json
├── plugins/
│   └── instavm/
│       ├── .claude-plugin/
│       │   └── plugin.json
│       └── skills/
│           └── use-instavm/
│               ├── agents/
│               │   └── openai.yaml
│               ├── references/
│               │   ├── access.md
│               │   ├── cli.md
│               │   ├── compute.md
│               │   ├── hosting.md
│               │   ├── platform.md
│               │   ├── setup.md
│               │   └── storage.md
│               └── SKILL.md
└── README.md
```

## Development Notes

- Keep `SKILL.md` concise and routing-focused.
- Keep workflow behavior in action-oriented references.
- Prefer installed CLI help and SDK method names over docs or memory.
- Keep CLI-specific guidance in `references/cli.md` rather than bloating the main skill file.

## References

- [Agent Skills CLI](https://skills.sh)
- [InstaVM](https://instavm.io)
- [InstaVM Python SDK docs](https://instavm.io/docs/sdks/python/overview)
- [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
