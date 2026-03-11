# Platform

Use advanced control-plane APIs and fall back to raw HTTP when the SDK is missing a needed feature.

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

Confirm request fields against the latest OpenAPI or docs before you use REST for newer features or SDK gaps.
