---
name: use-instavm
description: >
  Use InstaVM to run short-lived sandboxes and durable VMs, host apps, manage
  storage, snapshots, shares, SSH access, desktop workflows, and platform
  APIs. Trigger this when the user mentions InstaVM, instavm.io, the `instavm`
  Python SDK or CLI, `ssh instavm.dev`, app hosting, or VM lifecycle work,
  even if they do not explicitly say "InstaVM".
allowed-tools: Bash(instavm:*), Bash(python3:*), Bash(pip:*), Bash(ssh:*), Bash(curl:*), Bash(which:*)
---

# Use InstaVM

InstaVM is a cloud platform for running short-lived sandboxes and durable VMs, then managing access, storage, snapshots, shares, and desktop workflows around them.
This skill helps with the practical operator path: create or manage compute, host apps, move data, connect over SSH, and use advanced platform APIs when needed.

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
3. Make sure `instavm` is installed before you rely on CLI or SDK paths. The package ships both surfaces.
4. Start with the documented command or helper for the task. Probe CLI help, SDK attributes, or live schema only if the expected path is missing, errors, or looks version-skewed.

Load `references/setup.md` for exact install, auth, and fallback-probe steps.

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
- `references/cli.md`: CLI discovery, stored auth, command groups, and terminal-native operator workflows.

## Execution rules

1. Make sure `instavm` is installed before using either surface. `pip install -U instavm` provides both the CLI and the Python SDK.
2. Trust the documented task path first: use the referenced CLI command or SDK helper, then read back state from the API after mutations.
3. Probe only on demand. Use CLI `--help` or SDK inspection when the expected path fails, a command is missing, or capability is unclear. Fetch live docs or schema only for genuine uncertainty or REST fallback.
4. Prefer CLI for short operator workflows that map cleanly to one command or a short sequence:
   auth, whoami, docs or billing, VM list/create/delete/clone, share management, SSH key management, desktop actions, and volume operations.
5. Prefer the SDK for orchestration-heavy tasks: session execution, file upload or download, service setup, deploy flows, loops or conditionals, or any task that benefits from structured Python control flow.
6. Use a session for short-lived execution. Use a VM for SSH, shares, mounted volumes, or user-facing hosting.
7. Keep egress narrow and shares private unless the user explicitly wants broader access.
8. For live infrastructure requests, a quick repo inspection is fine, but do not do multi-minute offline scaffolding before auth is confirmed.
9. After mutation, read the resource back. If a field is ignored or missing in the follow-up state, treat that capability as unsupported in the current environment.
10. If CLI and SDK disagree, trust the path that succeeds and can be confirmed with a follow-up read-back.
11. If neither CLI nor SDK covers the task, use raw HTTP only after checking the latest schema.

## Composition patterns

- **Create, inspect, or delete infrastructure quickly**: setup -> cli
- **Host a static site or small web app**: setup -> hosting -> access
- **Run code or move files inside a machine**: setup -> compute
- **Create a reusable base image**: setup -> compute
- **Create a persistent worker**: setup -> storage -> access
- **Handle a CLI or SDK gap**: relevant operational reference -> platform

## Response format

For operational responses, return:

1. What was done and where.
2. The result: IDs, URLs, status, or key output.
3. What to do next, or confirmation that the task is complete.
