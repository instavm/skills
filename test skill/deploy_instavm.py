#!/usr/bin/env python3
import os
import sys
import time
from pathlib import Path
from urllib.request import urlopen

from instavm import InstaVM


APP_DIR = "/app/hello-world"
PORT = 8080


def require_api_key() -> str:
    api_key = os.environ.get("INSTAVM_API_KEY") or os.environ.get("INSTA_API_KEY")
    if not api_key:
        print("Missing INSTAVM_API_KEY or INSTA_API_KEY", file=sys.stderr)
        sys.exit(1)
    return api_key


def unwrap_url(payload):
    if isinstance(payload, dict):
        for key in ("url", "app_url", "share_url"):
            value = payload.get(key)
            if value:
                return value
    if isinstance(payload, str):
        return payload
    return None


def wait_for_http(url: str, attempts: int = 15) -> None:
    for attempt in range(1, attempts + 1):
        try:
            with urlopen(url, timeout=10) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(min(3 * attempt, 15))
    print(f"Timed out waiting for {url}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    project_root = Path(__file__).resolve().parent
    index_path = project_root / "index.html"
    if not index_path.exists():
        print(f"Missing app file: {index_path}", file=sys.stderr)
        sys.exit(1)

    client = InstaVM(api_key=require_api_key(), timeout=300)
    client.execute(f"mkdir -p {APP_DIR}", language="bash")
    client.upload_file(str(index_path), f"{APP_DIR}/index.html")
    client.execute_async(
        f"python3 -m http.server {PORT} --directory {APP_DIR}",
        language="bash",
        timeout=86400,
    )

    app_url = unwrap_url(client.get_session_app_url(port=PORT))
    if not app_url:
        print("Could not determine session app URL", file=sys.stderr)
        sys.exit(1)

    wait_for_http(app_url)

    session = client.get_session_info()
    print(f"session_id={session.get('session_id') or client.session_id}")
    print(f"share_url={app_url}")


if __name__ == "__main__":
    main()
