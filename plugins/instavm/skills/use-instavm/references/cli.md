# CLI

The installed `instavm` CLI is a first-class surface for terminal-native InstaVM workflows.
Use it when it shortens the path and keeps the result easy to read back.

## Discovery

Only use the CLI if it actually exists in the environment:

```bash
command -v instavm
instavm --version
```

`ssh instavm.dev ...` is also a valid command-line surface when it is configured locally.

Do not infer CLI commands from old examples or stale memory.
Start with the documented command for the task. Use `instavm --help` or `instavm <subcommand> --help` only when you hit uncertainty, a missing command, or version skew.

## Auth and identity

For quick setup and account checks, start here:

```bash
instavm auth status
instavm auth set-key
instavm whoami
```

- `instavm auth set-key` stores the API key in `~/.instavm/config.json`.
- `INSTAVM_API_KEY` still works well for non-interactive runs or ephemeral environments.
- If the CLI already has a stored key and `instavm whoami` succeeds, prefer the CLI for short operator tasks before reaching for Python.

## Command groups

The packaged CLI currently covers:

- `auth`: stored API-key management with `set-key`, `status`, and `logout`
- `whoami`: current account and SSH-key registrations
- `create|new`, `ls|list`, `rm|delete`, `clone`, `connect`: VM lifecycle and SSH access
- `snapshot`: list, inspect, build, create, and delete snapshots
- `share`: create and manage VM shares
- `ssh-key|sshkey`: list, add, and remove SSH keys
- `desktop`: status, start, stop, and viewer handoff for computer-use desktops
- `volume|volumes`: volumes, checkpoints, and file operations
- `doc|docs`, `billing`: documentation and billing links

## Selection rules

- Prefer CLI when it can do the job in fewer steps than the SDK and the output is easy to read back.
- Prefer the SDK when you need session execution, uploads, service setup, repeated in-VM commands, precise structured calls, or Python control flow.
- Use raw HTTP only when neither CLI nor SDK covers the task.
- If CLI and SDK disagree, trust the path that succeeds and can be confirmed with a follow-up read-back.

## Workflow handoff

Use the CLI to get into a good operating state, then switch references as needed:

- [setup.md](setup.md) for install, auth, and compute selection
- [hosting.md](hosting.md) when the task becomes a deploy flow with file transfer, daemon setup, or service verification
- [compute.md](compute.md) for execution, snapshots, and clones
- [access.md](access.md) for SSH, shares, and egress
- [storage.md](storage.md) for volumes
- [platform.md](platform.md) for advanced APIs and REST fallback
