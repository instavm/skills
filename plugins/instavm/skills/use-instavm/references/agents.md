# OpenAI Agents

Create agents on InstaVM through the OpenAI Agents SDK sandbox provider when the task is agent execution, not just raw VM or session management.

## When to use this reference

- The user wants to build, create, run, or host an agent on InstaVM and did not name a different agent framework.
- The user wants to build or run an OpenAI Agent whose tools execute in a cloud sandbox.
- The task needs per-agent filesystem, shell, networking, or snapshot support.
- The task needs multi-phase agent workflows with resume, volumes, or restricted egress.

Use `setup.md` first for install and auth. Pair this reference with `storage.md` for persistent data or `access.md` when the sandbox must expose ports.

## Install

```bash
pip install "instavm[agents]"
```

This installs the OpenAI Agents integration and auto-registers InstaVM as a sandbox provider.

## Minimal sandbox agent

```python
import asyncio
import os

from agents import RunConfig, Runner
from agents.sandbox import SandboxAgent, SandboxRunConfig
from instavm.integrations.openai_agents import (
    InstaVMSandboxClient,
    InstaVMSandboxClientOptions,
)

agent = SandboxAgent(
    name="Analyst",
    model="gpt-5.4",
    instructions="Inspect the workspace and answer concisely.",
)

async def main() -> None:
    client = InstaVMSandboxClient(api_key=os.environ["INSTAVM_API_KEY"])
    result = await Runner.run(
        agent,
        "What files are in the workspace?",
        run_config=RunConfig(
            sandbox=SandboxRunConfig(
                client=client,
                options=InstaVMSandboxClientOptions(memory_mb=1024),
            ),
        ),
    )
    print(result.final_output)

asyncio.run(main())
```

Each agent run gets its own InstaVM-backed sandbox VM session.

## Seed files with a manifest

Use a manifest when the agent needs known starting files:

```python
from agents.sandbox import Manifest, SandboxAgent
from agents.sandbox.entries import File

agent = SandboxAgent(
    name="CSV Analyst",
    model="gpt-5.4",
    instructions="Analyze the provided CSV.",
    default_manifest=Manifest(
        entries={
            "data.csv": File(content=b"region,revenue\nnorth,120000\nsouth,95000\n"),
        }
    ),
)
```

Prefer this over ad hoc bootstrap shell commands for small deterministic inputs.

## Tune the sandbox

`InstaVMSandboxClientOptions(...)` is the main control point:

```python
options = InstaVMSandboxClientOptions(
    memory_mb=2048,
    vcpu_count=2,
    snapshot_id="snap_abc123",
    snapshot_on_terminate=True,
    snapshot_name="agent-checkpoint",
    allow_internet_access=False,
    allow_package_managers=True,
    allowed_domains=("api.openai.com",),
    env={"APP_ENV": "prod"},
    metadata={"project": "agent-demo"},
)
```

Use this to size the VM, boot from a snapshot, lock down egress, or tag runs for later inspection.

## Resume a prior sandbox

For multi-phase agent workflows, deserialize the prior session state and pass it back in:

```python
resume_state = result1._sandbox_resume_state
session_state = client.deserialize_session_state(resume_state["session_state"])

result2 = await Runner.run(
    reviewer,
    "Review the code the builder wrote.",
    run_config=RunConfig(
        sandbox=SandboxRunConfig(client=client, session_state=session_state),
    ),
)
```

Use this for builder -> reviewer or planner -> executor handoffs without losing the workspace.

## Add persistent storage

For data that must survive across separate sandbox runs, create a volume and mount it through the session:

```python
from instavm import InstaVM

raw_client = InstaVM(api_key=api_key, auto_start_session=False)
volume = raw_client.volumes.create("shared-data", quota_bytes=1_073_741_824)

session = await sandbox_client.create(options=options)
inner = session._inner
await inner.mount_volume(volume["id"], "/mnt/shared-data")
```

Use `storage.md` for the full volume lifecycle.

## Expose ports only when the task needs it

If an agent-run service must be reachable from outside the sandbox, pair this reference with `access.md`. Keep shares private and egress narrow unless the user explicitly wants public reachability.

## Execution rules for agent tasks

1. Confirm both `INSTAVM_API_KEY` and `OPENAI_API_KEY` for live runs.
2. Prefer `SandboxAgent` plus `SandboxRunConfig` over custom VM bootstrapping when the user wants an agent on InstaVM and has not explicitly named another agent framework.
3. Start with the smallest viable `InstaVMSandboxClientOptions(...)` payload, then add snapshots, volumes, or egress rules only when needed.
4. Use resume state for multi-phase workflows before reaching for custom persistence.
5. Use `storage.md` when state must outlive a single resumed sandbox chain.
