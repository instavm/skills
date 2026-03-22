---
name: use-instavm
description: >
  Operate InstaVM infrastructure: run ephemeral sessions, create or manage VMs,
  host or deploy apps, take snapshots, clone machines, register SSH keys,
  expose shares, set egress, mount volumes, and use platform APIs. Use this
  whenever the user mentions InstaVM, instavm.io, the `instavm` Python SDK,
  `ssh instavm.dev`, app hosting, or VM lifecycle work, even if they do not
  explicitly say "InstaVM".
allowed-tools: Bash(instavm:*), Bash(python3:*), Bash(pip:*), Bash(ssh:*), Bash(curl:*), Bash(which:*)
---

# Use InstaVM

Manage VMs, sessions, snapshots, shares, volumes, and platform APIs on InstaVM infrastructure.

## InstaVM resource model

- **Session** is a short-lived execution sandbox.
- **VM** is a durable machine for longer-running work, SSH access, shares, or mounted volumes.
- **Snapshot** is a reusable machine image created from a VM or an OCI image.
- **Share** exposes a port from a session or VM.
- **Volume** is persistent storage mounted into a VM.
- **Platform APIs** include computer-use, audit, webhooks, API keys, and related control-plane features.

## Preflight

Before any mutation:

1. For live deploy, host, create, update, snapshot, or delete requests, verify authentication first.
2. If no API key or authenticated CLI path is available, stop and ask for credentials.
   Do not spend time generating deploy scripts, repo changes, or long offline setup
   unless the user explicitly asks for offline preparation.
3. After auth is confirmed, probe the installed SDK surface before assuming helper names.
4. If a native `instavm` CLI exists later, prefer it only when it is clearly the shortest path.

Load `references/setup.md` for exact install, auth, and surface-probe steps.

## Routing

Load only the reference you need. Two references are usually enough, even for multi-step tasks.

- `references/setup.md`: install, auth, choose session vs VM, create or delete compute.
- `references/hosting.md`: host or deploy an app, including static sites,
  simple web apps, long-lived servers, shares, and deploy verification.
- `references/compute.md`: run code, transfer files, snapshot, clone, or build from OCI.
- `references/access.md`: connect to a machine or expose it to the network.
- `references/storage.md`: persist or move data with volumes, checkpoints, and mounts.
- `references/platform.md`:
  advanced APIs and REST fallback.
- `references/cli.md`: prefer or inspect a future native CLI.

## Execution rules

1. Trust the live product surface over skill text: start with the installed SDK, actual CLI help if a CLI exists, and read-back state from the API after mutations.
2. Detect capability before use. For SDK, inspect attributes or method signatures.
   For CLI, use `--help` only if the binary exists.
   Fetch the latest OpenAPI or live docs only when capability is unclear,
   a field may be unsupported, or you need a REST fallback.
3. Use a session for short-lived execution. Use a VM for SSH, shares, mounted volumes, or user-facing hosting.
4. Keep egress narrow and shares private unless the user explicitly wants broader access.
5. For live infrastructure requests, a quick repo inspection is fine, but do not do multi-minute offline scaffolding before auth is confirmed.
6. After mutation, read the resource back. If a field is ignored or missing in the follow-up state, treat that capability as unsupported in the current environment.
7. If the installed SDK lacks the needed helper, use raw HTTP only after checking the latest schema.

## Composition patterns

- **Bootstrap a working VM**: setup -> compute -> access
- **Host a static site or small web app**: setup -> hosting -> access
- **Create a reusable base image**: setup -> compute
- **Create a persistent worker**: setup -> storage -> access
- **Handle an SDK gap**: relevant operational reference -> platform
- **Add future CLI support**: cli -> relevant operational reference

## Response format

For operational responses, return:

1. What was done and where.
2. The result: IDs, URLs, status, or key output.
3. What to do next, or confirmation that the task is complete.
