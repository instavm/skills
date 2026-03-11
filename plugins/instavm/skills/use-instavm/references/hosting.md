# Hosting

Host a static site or small app on InstaVM without rediscovering the same deployment traps.

## Choose the deployment path

- For a static site or simple web app, use a durable VM plus a long-running process and a share.
- If you can bind a VM `session_id` back onto the SDK, prefer SDK upload and execution over SSH file transfer.
- Use SSH mainly for manual inspection or when the SDK path is unavailable.

## Recommended static hosting flow

1. Create a VM with an explicit lifetime.
2. Read back the VM record and capture `vm_id`, `status`, and `session_id`.
3. Bind `client.session_id` to that VM session when possible.
4. Upload files with `upload_file(...)`.
5. Start the web server with `execute_async(...)`, not `nohup ... &`.
6. Create a public share for the port.
7. Verify the share externally with `curl -I`.
8. Tighten egress after upload if the app does not need outbound access.

## VM lifetime rule

Never rely on the default lifetime for user-facing hosting. Set `vm_lifetime_seconds` explicitly or update it immediately after creation.

```python
vm = client.vms.create(wait=True, vm_lifetime_seconds=604800)
vm_id = vm["vm_id"]
vm = client.vms.get(vm_id)
```

If create accepts only a simpler payload, create the VM first, then patch lifetime or metadata with `client.vms.update(...)`.

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

## Start long-lived servers correctly

Do not assume `execute(..., language="bash")` behaves like a persistent login shell. Backgrounding with `nohup ... &` can fail or exit unexpectedly depending on the runner.

Prefer `execute_async(...)` with a foreground server:

```python
server_code = r'''
import functools
import http.server
import socketserver

PORT = 8080
DIRECTORY = "/app/music-maker"
Handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=DIRECTORY)

with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
    print(f"serving {DIRECTORY} on port {PORT}", flush=True)
    httpd.serve_forever()
'''

task = client.execute_async(server_code, language="python", timeout=604800)
```

Then confirm the task is still running before you claim success.

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
