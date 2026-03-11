---
name: instavm
description: Use this skill when you need to create or manage InstaVM sessions, VMs, snapshots, SSH access, shares, egress policies, or volumes. Prefer the Python SDK, probe the installed client surface first, and fall back to the REST API when the local package lags the docs or OpenAPI.
---

# InstaVM

Use this skill for hands-on InstaVM operations. Default to the least durable primitive that solves the task, keep egress narrow, and clean up anything you create unless the user asks to keep it.

## When To Use

- run code in an ephemeral sandbox
- create, inspect, update, clone, snapshot, or delete VMs
- register SSH keys and connect to a VM
- expose a port with a share
- set session or VM egress rules
- create volumes, upload files, checkpoint them, and mount them into a VM
- use platform APIs such as computer-use, webhooks, audit, or API keys

## Operating Rules

- Use a session for short-lived execution that does not need SSH or persistent storage.
- Use `client.vms.*` for durable machines, SSH access, shares, or attached volumes.
- Use `client.vms.snapshot(...)` for a configured running VM.
- Use `client.snapshots.create(...)` for a reusable base built from an OCI image.
- Prefer private shares and restrictive egress unless the user explicitly wants broader access.
- Trust the installed SDK over docs, tests, or memory.

## Setup

1. Ensure an API key is available. Prefer `INSTAVM_API_KEY`; if the repo already uses `INSTA_API_KEY`, follow local convention.
2. Install or upgrade the SDK:

```bash
pip install -U instavm
```

3. Probe the installed surface before assuming helper names:

```python
import os
from instavm import InstaVM

api_key = os.environ.get("INSTAVM_API_KEY") or os.environ["INSTA_API_KEY"]
client = InstaVM(api_key=api_key)

for name in ["vms", "snapshots", "shares", "volumes", "computer_use", "api_keys", "audit", "webhooks"]:
    print(name, hasattr(client, name))

for name in ["set_session_egress", "set_vm_egress", "add_ssh_key"]:
    print(name, hasattr(client, name))
```

Unless a snippet says otherwise, the remaining examples assume `client` and `vm_id` already exist.

## Compatibility Rule

Current SDK surfaces can drift.

- Newer source branches expose `client.volumes.*` plus `client.vms.mount_volume()`, `client.vms.list_volumes()`, and `client.vms.unmount_volume()`.
- SSH and egress are most portable today as top-level methods: `add_ssh_key()`, `list_ssh_keys()`, `delete_ssh_key()`, `set_session_egress()`, `get_session_egress()`, `set_vm_egress()`, `get_vm_egress()`.
- Do not assume `client.ssh` or `client.egress` managers exist unless `hasattr` confirms them.
- If the installed package is missing a needed feature, check the latest schema and use raw HTTP instead of guessing method names.

## Core Workflows

### Ephemeral Session

```python
with InstaVM(api_key=api_key, timeout=300) as client:
    result = client.execute("python -V", language="bash")
    print(result)
```

### Durable VM

```python
vm = client.vms.create(
    wait=True,
    vm_lifetime_seconds=3600,
    memory_mb=2048,
    vcpu_count=4,
    metadata={"project": "agent-task"},
)

vm_id = vm["vm_id"]
print(vm_id)
```

### Snapshot And Clone

```python
snapshot = client.vms.snapshot(vm_id=vm_id, wait=True, name="configured-env")
clone = client.vms.clone(vm_id=vm_id, wait=True, snapshot_name="clone-point")
```

To build a base image from an OCI image:

```python
base = client.snapshots.create(
    oci_image="docker.io/library/python:3.11-slim",
    name="python-3-11-base",
    vcpu_count=2,
    memory_mb=1024,
    snapshot_type="user",
    build_args={
        "extra_apt_packages": "git ffmpeg",
        "extra_pip_packages": "numpy pandas",
        "git_clone_url": "https://github.com/example/repo.git",
        "git_clone_branch": "main",
    },
)
```

### SSH

Register a public key:

```python
from pathlib import Path

public_key = Path("~/.ssh/id_ed25519.pub").expanduser().read_text().strip()
client.add_ssh_key(public_key)
```

Then connect:

```bash
ssh -i ~/.ssh/id_ed25519 <vm_id>@instavm.dev
```

If the local machine already has InstaVM's SSH workflow configured, these shortcuts may also work:

```bash
ssh instavm.dev create
ssh instavm.dev ls
ssh instavm.dev clone <vm_id>
```

### Egress

Use the narrowest policy that still allows the workload to succeed.

```python
client.set_vm_egress(
    vm_id,
    allow_package_managers=True,
    allow_http=False,
    allow_https=True,
    allowed_domains=["api.example.com", "pypi.org", "files.pythonhosted.org"],
    allowed_cidrs=[],
)
```

For an execution session instead of a durable VM:

```python
client.set_session_egress(
    allow_package_managers=True,
    allow_http=False,
    allow_https=True,
    allowed_domains=["pypi.org", "files.pythonhosted.org"],
)
```

### Shares

```python
share = client.shares.create(vm_id=vm_id, port=3000, is_public=False)
client.shares.update(share_id=share["share_id"], is_public=True)
```

### Volumes

If `client.volumes` exists, prefer it over raw HTTP:

```python
volume = client.volumes.create(name="project-data", quota_bytes=10 * 1024 * 1024 * 1024)
volume_id = volume["id"]

client.volumes.upload_file(volume_id, file_path="./train.csv", path="datasets/train.csv", overwrite=True)
checkpoint = client.volumes.create_checkpoint(volume_id, name="before-training")

client.vms.mount_volume(
    vm_id,
    volume_id,
    mount_path="/data",
    mode="rw",
    checkpoint_id=checkpoint["id"],
    wait=True,
)

print(client.vms.list_volumes(vm_id))
client.vms.unmount_volume(vm_id, volume_id, mount_path="/data", wait=True)
```

```python
client.volumes.list(refresh_usage=True)
client.volumes.get(volume_id, refresh_usage=True)
client.volumes.list_files(volume_id, prefix="datasets/", recursive=True, limit=1000)
client.volumes.download_file(volume_id, path="datasets/train.csv", local_path="./train.csv")
```

## REST Fallback

Use raw HTTP only when the installed SDK lacks the needed helper:

```python
import os
import requests

api_key = os.environ.get("INSTAVM_API_KEY") or os.environ["INSTA_API_KEY"]
headers = {"X-API-Key": api_key}

response = requests.post(
    "https://api.instavm.io/v1/vms",
    headers=headers,
    params={"wait": "true"},
    json={"vm_lifetime_seconds": 3600, "memory_mb": 2048, "vcpu_count": 4},
)
response.raise_for_status()
print(response.json())
```

Confirm exact request fields against the latest OpenAPI or docs before doing this for newer features such as volumes.

## Cleanup

- close or kill sessions you create
- delete temporary VMs, volumes, or snapshots unless the user wants them preserved
- revoke temporary shares or SSH keys when they are no longer needed
- restore tighter egress after setup if you broadened it

## References

- OpenAPI: [staging.instavm.io/openapi.json](https://staging.instavm.io/openapi.json)
- PyPI: [pypi.org/project/instavm](https://pypi.org/project/instavm/)
- Python SDK docs: [instavm.io/docs/sdks/python/overview](https://instavm.io/docs/sdks/python/overview)
