# Storage

Create volumes, move files through them, checkpoint them, and mount them into VMs.

## Volume lifecycle

```python
volume = client.volumes.create(name="project-data", quota_bytes=10 * 1024 * 1024 * 1024)
volume_id = volume["id"]

client.volumes.list(refresh_usage=True)
client.volumes.get(volume_id, refresh_usage=True)
client.volumes.update(volume_id, name="project-data-v2", quota_bytes=20 * 1024 * 1024 * 1024)
```

Delete only when the user wants the data gone:

```python
client.volumes.delete(volume_id)
```

## File operations

```python
client.volumes.upload_file(volume_id, file_path="./train.csv", path="datasets/train.csv", overwrite=True)
client.volumes.list_files(volume_id, prefix="datasets/", recursive=True, limit=1000)
client.volumes.download_file(volume_id, path="datasets/train.csv", local_path="./train.csv")
client.volumes.delete_file(volume_id, path="datasets/train.csv")
```

## Checkpoints

```python
checkpoint = client.volumes.create_checkpoint(volume_id, name="before-training")
client.volumes.list_checkpoints(volume_id)
client.volumes.delete_checkpoint(volume_id, checkpoint["id"])
```

Use checkpoints before risky mutations or before handing off a reusable state.

## Mount into a VM

```python
client.vms.mount_volume(
    vm_id,
    volume_id,
    mount_path="/data",
    mode="rw",
    checkpoint_id=checkpoint["id"],
    wait=True,
)

client.vms.list_volumes(vm_id)
client.vms.unmount_volume(vm_id, volume_id, mount_path="/data", wait=True)
```

If the installed package lacks `client.volumes` or the VM mount helpers, switch to the REST API only after confirming the current schema.
