# Setup

Install and authenticate the SDK, probe the client surface, and create the right compute primitive.

## Install and auth

```bash
pip install -U instavm
```

Use `INSTAVM_API_KEY` when possible. If the local repo already uses `INSTA_API_KEY`, follow that convention instead of fighting it.

Probe the installed client before you assume helper names:

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

## Choose a primitive

- Use a **session** for one-off execution that does not need SSH or persistent storage.
- Use a **VM** for long-running work, SSH access, exposed ports, or mounted volumes.

## Sessions

```python
from instavm import InstaVM

with InstaVM(api_key=api_key, timeout=300) as client:
    result = client.execute("python -V", language="bash")
    print(result)
    print(client.get_session_info())
    print(client.get_usage())
```

Useful session helpers:

```python
client.get_session_info()
client.get_session_app_url()
client.list_sandboxes()
client.kill()
client.close_session()
```

## VMs

Create a durable VM:

```python
vm = client.vms.create(
    wait=True,
    vm_lifetime_seconds=3600,
    memory_mb=2048,
    vcpu_count=4,
    metadata={"project": "agent-task"},
)

vm_id = vm["vm_id"]
vm = client.vms.get(vm_id)
```

Inspect or mutate it:

```python
client.vms.list()
client.vms.get(vm_id)
client.vms.update(vm_id, metadata={"project": "agent-task", "owner": "agent"})
client.vms.delete(vm_id)
```

Use a read-back call after mutation so the user gets the resulting state, not just the action attempt.

## VM creation gotchas

- Do not rely on the default VM lifetime. Set `vm_lifetime_seconds` explicitly for anything user-facing.
- After creation, read back the VM record and keep `vm_id`, `status`, and `session_id` if the API returns them.
- If a rich create payload is rejected, do not guess field combinations repeatedly. Capture the real validation body, retry with a minimal create payload, then patch fields with `client.vms.update(...)`.

Minimal fallback:

```python
vm = client.vms.create(wait=True, vm_lifetime_seconds=86400)
vm_id = vm["vm_id"]
client.vms.update(vm_id, metadata={"project": "agent-task"})
vm = client.vms.get(vm_id)
```
