# Access

Connect to machines, expose them externally, and control network reachability.

## SSH

Register a public key:

```python
from pathlib import Path

public_key = Path("~/.ssh/id_ed25519.pub").expanduser().read_text().strip()
client.add_ssh_key(public_key)
```

Inspect or remove keys:

```python
client.list_ssh_keys()
client.delete_ssh_key(key_id)
```

Then connect:

```bash
ssh -i ~/.ssh/id_ed25519 <vm_id>@instavm.dev
```

If the local machine already has InstaVM's SSH shortcuts configured, these may also work:

```bash
ssh instavm.dev create
ssh instavm.dev ls
ssh instavm.dev clone <vm_id>
```

## Shares

Expose a port from a VM:

```python
share = client.shares.create(vm_id=vm_id, port=3000, is_public=False)
client.shares.update(share_id=share["share_id"], is_public=True)
```

For ephemeral apps, use `session_id` instead of `vm_id`.

## Egress

Keep egress as narrow as the workload allows.

For a VM:

```python
client.set_vm_egress(
    vm_id,
    allow_package_managers=True,
    allow_http=False,
    allow_https=True,
    allowed_domains=["api.example.com", "pypi.org", "files.pythonhosted.org"],
    allowed_cidrs=[],
)

client.get_vm_egress(vm_id)
```

For a session:

```python
client.set_session_egress(
    allow_package_managers=True,
    allow_http=False,
    allow_https=True,
    allowed_domains=["pypi.org", "files.pythonhosted.org"],
)

client.get_session_egress()
```

## Custom domains

```python
domain = client.custom_domains.create(
    domain="app.example.com",
    share_id=share["share_id"],
    dns_provider="cloudflare",
    dns_credentials={"api_token": "..."},
)

client.custom_domains.list()
client.custom_domains.health(domain["id"])
client.custom_domains.verify(domain["id"])
client.custom_domains.delete(domain["id"])
```

Use custom domains only when the user actually needs a stable hostname.
