# Hosting

Host a static site or small app on InstaVM without rediscovering the same deployment traps.

## Choose the deployment path

- For a static site or simple web app, use a durable VM plus a boot-persistent daemon service and a share.
- If you can bind a VM `session_id` back onto the SDK, prefer SDK upload and execution over SSH file transfer.
- Use SSH mainly for manual inspection or when the SDK path is unavailable.

## Credential gate

If the user asked for a live deployment, verify auth before you write deploy scripts, change the repo, or spend time on detailed packaging work.

- A quick repo inspection to identify static vs dynamic hosting is fine.
- If there is no API key or authenticated CLI path, stop and ask for credentials.
- Only prepare offline deployment assets when the user explicitly asks for a script, template, or dry run.

## Recommended static hosting flow

1. Create a VM with an explicit lifetime.
2. Read back the VM record and capture `vm_id`, `status`, and `session_id`.
3. Bind `client.session_id` to that VM session when possible.
4. Upload files with `upload_file(...)`.
5. Install and enable a daemon service for the app.
6. Create a public share for the port.
7. Verify the daemon really starts and survives a restart.
8. Verify the share externally with `curl -I`.
9. Tighten egress after upload if the app does not need outbound access.

## VM lifetime rule

Never rely on the default lifetime for user-facing hosting. Set `vm_lifetime_seconds` explicitly at create time. Only use `client.vms.update(..., vm_lifetime_seconds=...)` after the live API or backend version clearly supports lifetime updates.

Keep the requested lifetime in one variable so future plan or product changes are one edit. For portable examples, use `86400` as the current safe baseline unless the live VM API or account docs say otherwise.

The local SDK documents `20-86400` for session-backed `InstaVM(timeout=...)`, but that is not the same thing as the managed VM lifetime contract. Use successful `client.vms.create(...)` behavior and a follow-up `client.vms.get(...)` read-back as the source of truth. Treat lifetime updates as optional capability, not a baseline assumption.

```python
requested_lifetime_seconds = 86400  # raise only if the live VM API for this account accepts it
vm = client.vms.create(wait=True, vm_lifetime_seconds=requested_lifetime_seconds)
vm_id = vm["vm_id"]
vm = client.vms.get(vm_id)
```

If create accepts only a simpler payload, create the VM first, then patch metadata or other confirmed-supported fields with `client.vms.update(...)`. If lifetime itself must change and update support is unclear, recreate the VM with the correct lifetime instead of assuming the patch will work.

## Prefer SDK upload over SSH copy

If the VM has a usable `session_id`, do this:

```python
vm = client.vms.get(vm_id)
client.session_id = vm["session_id"]

client.execute("mkdir -p /app/music-maker/examples", language="bash")
client.upload_file("./index.html", "/app/music-maker/index.html")
client.upload_file("./app.js", "/app/music-maker/app.js")
client.upload_file("./styles.css", "/app/music-maker/styles.css")
```

This avoids `scp` issues through the SSH proxy layer.

If you must use SSH and `scp` fails, use tar-over-SSH before you spend time debugging the SCP subsystem.

## Writable path rule

Do not assume `/app` is writable over SSH.

- SDK session operations may write into `/app`
- SSH may log in as a non-root user that cannot write there

For SSH-driven deployments, use `~/app-name` unless you have already changed `/app` ownership.

## Python path on VMs

Always use `/usr/local/bin/python3` — this is the correct Python (3.13) on InstaVM VMs. Use it in `ExecStart` in service files and in any direct shell invocations. Only fall back to probing with `which python3` if `/usr/local/bin/python3` doesn't exist.

## Installing packages

Use `python3 -m pip` — the pip binary may not be on PATH but the module works:

```bash
/usr/local/bin/python3 -m pip install flask dspy-ai openai --quiet
```

Many system binaries (`tail`, `grep`, `apt-get`) may fail with `Exec format error` in bash. Avoid pipes — do any filtering in Python instead, or run commands separately.

## Run the app as a daemon service

For hosted apps, do not leave the server tied to a one-off shell. Install a service that restarts on boot so VM restart features work without manual intervention.

Prefer `systemd` when it is available and you have the needed permissions. Keep the app under a stable path and point the service at that path.

**Always use `/usr/local/bin/python3`** in `ExecStart`, not `/usr/bin/python3`.

**Write the service file via Python** to avoid shell escaping issues:

```python
svc = """[Unit]
Description=my-app
After=network.target

[Service]
WorkingDirectory=/app/my-app
Environment=MY_VAR=value
ExecStart=/usr/local/bin/python3 /app/my-app/app.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
"""
client.execute(
    f'python3 -c "open(\'/etc/systemd/system/my-app.service\', \'w\').write({repr(svc)})"',
    language="bash"
)
```

Typical bootstrapping flow (run as separate execute calls, not piped):

```python
client.execute("systemctl daemon-reload", language="bash")
client.execute("systemctl enable --now my-app.service", language="bash")
client.execute("systemctl status --no-pager my-app.service", language="bash")
```

**Verify systemd actually works first** — in some VM environments systemctl crashes with segfaults or illegal instruction errors. If that happens, fall back to `execute_async(...)`.

Then verify restart behavior before you claim success:

```python
client.execute("systemctl restart my-app.service", language="bash")
# curl via Python since /usr/bin/curl may also be broken
client.execute("""
import urllib.request
try:
    r = urllib.request.urlopen('http://127.0.0.1:8080/', timeout=5)
    print('HTTP', r.status)
except Exception as e:
    print('ERROR', e)
""", language="python")
```

Use `execute_async(...)` as a fallback when systemd is unavailable or crashes.

## Expose and verify

```python
share = client.shares.create(port=8080, vm_id=vm_id, is_public=True)
print(share)
```

Verify from outside the VM:

```bash
curl -I --max-time 20 https://<share-host>.instavm.site/
```

Do not stop at "share created". Confirm HTTP 200 or the actual expected response.

## Stable URL rule

Share URLs are disposable. They change across redeploys and disappear when the backing VM or session dies.

- For a temporary demo, a share is fine.
- For anything user-facing, either keep the VM lifetime correct or add a custom domain after the app is stable.

## Static app hardening

After a static site is live:

```python
client.set_vm_egress(
    vm_id,
    allow_package_managers=False,
    allow_http=False,
    allow_https=False,
    allowed_domains=[],
    allowed_cidrs=[],
)
```

Verify the share still serves after the egress change.
