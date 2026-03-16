# Platform

Use advanced control-plane APIs and fall back to raw HTTP when the SDK is missing a needed feature.

## Compatibility precedence

When product surfaces disagree, use this order:

1. Successful live CLI or SDK behavior plus a read-back call
2. Latest OpenAPI or live docs
3. Local docs, tests, or repo examples
4. Skill text

Do not assume a `200` means a field was applied. If a follow-up `get`, `list`, or equivalent state read does not show the change, treat the field as unsupported or ignored in that environment.

## When to fetch OpenAPI or docs

Do not fetch OpenAPI on every InstaVM task. Load it only when one of these is true:

1. The installed SDK is missing the helper you need.
2. A field or route may be unsupported and you need to confirm the live contract.
3. CLI output, SDK behavior, and local examples disagree.
4. You need a raw REST call for a newer feature.

Default order:

1. Inspect the installed SDK
2. Try the live capability with a safe read or create call
3. Read the latest OpenAPI or live docs if the contract is still unclear
4. Fall back to raw HTTP

## Computer-use and browser

Computer-use viewer:

```python
viewer = client.computer_use.viewer_url(session_id)
state = client.computer_use.get(session_id, "/state")
```

Browser automation:

```python
session = client.browser.create_session(viewport_width=1366, viewport_height=768)
session.navigate("https://example.com")
session.screenshot(full_page=True)
session.close()
```

## API keys

```python
client.api_keys.create(description="ci key")
client.api_keys.list()
client.api_keys.get(item_id)
client.api_keys.update(item_id, description="rotated key")
client.api_keys.delete(item_id)
```

## Audit

```python
client.audit.catalog()
client.audit.events(limit=25, status="success")
client.audit.get_event(event_id)
```

## Webhooks

```python
endpoint = client.webhooks.create_endpoint(
    url="https://example.com/instavm/webhook",
    event_patterns=["vm.*", "snapshot.*"],
)

client.webhooks.list_endpoints()
client.webhooks.get_endpoint(endpoint["id"])
client.webhooks.verify_endpoint(endpoint["id"])
client.webhooks.rotate_secret(endpoint["id"])
client.webhooks.list_deliveries(limit=10)
client.webhooks.replay_delivery(delivery_id)
```

## REST fallback

Use raw HTTP only when the installed SDK surface is missing the helper you need:

```python
import os
import requests

api_key = os.environ.get("INSTAVM_API_KEY") or os.environ["INSTA_API_KEY"]
headers = (
    {"X-API-Key": api_key}
    if api_key.startswith("instavm_sk_")
    else {"Authorization": f"Bearer {api_key}"}
)

response = requests.post(
    "https://api.instavm.io/v1/vms",
    headers=headers,
    params={"wait": "true"},
    json={"vm_lifetime_seconds": 3600, "memory_mb": 2048, "vcpu_count": 4},
)
response.raise_for_status()
print(response.json())
```

For `instavm_sk_...` API keys, prefer `X-API-Key` first. Do not assume `Authorization: Bearer ...` will work for API-key-backed endpoints.

Confirm request fields against the latest OpenAPI or docs before you use REST for newer features or SDK gaps. After any REST mutation, follow with a read-back request before you report success.
