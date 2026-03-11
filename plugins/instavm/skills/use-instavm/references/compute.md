# Compute

Run commands, move files through a session, and capture reusable machine state.

## Bind a created VM back onto the session helpers

Some SDK surfaces expose `execute()` and `upload_file()` for sessions, while VM lifecycle lives under `client.vms.*`. When a created VM has a usable `session_id`, bind it back onto the client instead of switching to brittle SSH copy flows.

```python
vm = client.vms.get(vm_id)
session_id = vm["session_id"]

client.session_id = session_id
client.execute("pwd && python3 --version", language="bash")
client.upload_file("./app.js", "/app/app.js")
```

If the VM record does not include `session_id`, inspect the latest session info before falling back to SSH.

## Execution

Simple execution:

```python
result = client.execute("python -V", language="bash")
print(result)
```

Async execution:

```python
task = client.execute_async("sleep 5 && echo done", language="bash")
result = client.get_task_result(task["task_id"], poll_interval=2, timeout=60)
print(result)
```

Streaming execution:

```python
for chunk in client.execute_streaming("python -u app.py"):
    print(chunk, end="")
```

## File movement through a session

```python
client.upload_file("local_script.py", "/app/local_script.py")
client.execute("python /app/local_script.py", language="bash")
client.download_file("output.json", local_path="./output.json")
```

Prefer this path over `scp` when you already have a valid session for the target VM.

## Snapshot a running VM

```python
snapshot = client.vms.snapshot(vm_id=vm_id, wait=True, name="configured-env")
clone = client.vms.clone(vm_id=vm_id, wait=True, snapshot_name="clone-point")
```

Use this when you already have a configured VM and want a reusable baseline or a copy.

## Build a snapshot from an OCI image

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

Then inspect or clean up:

```python
client.snapshots.list(snapshot_type="user")
client.snapshots.get(base["id"])
client.snapshots.delete(base["id"])
```

For OCI-based builds, poll status until it reaches a terminal state before you claim success.
