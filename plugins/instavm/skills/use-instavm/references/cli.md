# CLI

This skill is SDK-first today, but keep a clean route for a future native `instavm` CLI.

## Discovery

Only use a native CLI if it actually exists in the environment:

```bash
command -v instavm
instavm --version
instavm --help
instavm <subcommand> --help
```

`ssh instavm.dev ...` is also a valid command-line surface when it is configured locally.

## Selection rule

- Prefer CLI when it can do the job in fewer steps than the SDK and the output is easy to read back.
- Prefer the SDK when you need precise structured calls, Python control flow, or features that are already exposed there.
- Use raw HTTP only when neither CLI nor SDK covers the task.

## Future expansion

When InstaVM ships a stable CLI surface, document its real commands here instead of expanding `SKILL.md`.

Until then, use:

- [setup.md](setup.md) for install, auth, and compute selection
- [compute.md](compute.md) for execution, snapshots, and clones
- [access.md](access.md) for SSH, shares, and egress
- [storage.md](storage.md) for volumes
- [platform.md](platform.md) for advanced APIs and REST fallback
