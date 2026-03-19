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

If SSH is denied but the account already has registered keys, do not assume `~/.ssh/id_ed25519` is the correct one. Match the account's registered public keys against local `~/.ssh/*.pub` files and use the private key for the matching public key.

## Identity and writable path gotcha

Do not assume the SSH user and the SDK execution user are the same.

- `execute()` / `upload_file()` may run as a root-backed session in `/app`
- SSH may log in as a non-root user such as `appuser` with `HOME=/home/appuser`
- SDK uploads are most reliable when staged under `/app`, then moved or extracted into the final path with a follow-up command

So `/app` can be writable via the SDK path but not writable over SSH.

Check before you deploy through SSH:

```bash
id
pwd
echo "HOME=$HOME"
stat -c "%A %U:%G %n" / /app "$HOME"
```

If you are deploying over SSH, prefer `~/...` unless you deliberately bootstrap `/app` ownership.

## Shares

Expose a port from a VM:

```python
share = client.shares.create(vm_id=vm_id, port=3000, is_public=False)
client.shares.update(share_id=share["share_id"], is_public=True)
```

For ephemeral apps, use `session_id` instead of `vm_id`.

After creating a share, verify it externally. A successful share creation call is not enough.

## Egress

Keep egress as narrow as the workload allows.

If you already know the outbound dependencies at provision time, prefer `egress_policy` on `client.vms.create(...)` so bootstrap steps do not fail before you get a chance to call `set_vm_egress(...)`.

At creation time:

```python
vm = client.vms.create(
    wait=True,
    vm_lifetime_seconds=3600,
    egress_policy={
        "allow_package_managers": True,
        "allow_http": False,
        "allow_https": True,
        "allowed_domains": ["registry.npmjs.org", "fonts.googleapis.com", "fonts.gstatic.com"],
        "allowed_cidrs": [],
    },
)
```

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

Share URLs are tied to the backing session or VM. If the compute dies, the share dies too. Use a custom domain only after the underlying VM lifetime is correct.
