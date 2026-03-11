# InstaVM Skill

Agent skill for InstaVM, following the Agent Skills format.

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

- `instavm`

`instavm` is operational and SDK-first. It tells agents when to use sessions vs durable VMs, how to work with snapshots, SSH, shares, egress, and volumes, and when to fall back to raw REST calls if the installed SDK lags the docs.

## Workflow Coverage

`instavm` covers:

- ephemeral code execution sessions
- durable VM lifecycle operations
- VM snapshots and clones
- OCI-image snapshot builds
- SSH key registration and SSH access
- share creation for exposed ports
- session and VM egress policy management
- volume creation, upload, checkpoint, mount, and unmount
- platform APIs such as computer-use, audit, webhooks, and API keys

## Repository Structure

```text
skill/
├── .claude-plugin/
│   └── marketplace.json
├── agents/
│   └── openai.yaml
├── SKILL.md
└── README.md
```

## Development Notes

- Keep `SKILL.md` concise and action-oriented.
- Prefer installed SDK method names over docs or memory.
- Use raw HTTP only when the installed SDK is missing the needed helper.
- Keep examples practical and easy for agents to adapt.

## References

- [Agent Skills CLI](https://skills.sh)
- [InstaVM](https://instavm.io)
- [InstaVM Python SDK docs](https://instavm.io/docs/sdks/python/overview)
- [Claude Code plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces)
