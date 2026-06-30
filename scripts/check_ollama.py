from __future__ import annotations

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"Accept": "application/json"})
    with urlopen(request, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def model_base_name(name: str) -> str:
    return name.split(":", 1)[0]


def has_model(models: list[str], expected: str) -> bool:
    return any(name == expected or model_base_name(name) == model_base_name(expected) for name in models)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local Ollama availability.")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama base URL")
    parser.add_argument("--model", default="techcorp-phi3-financial", help="Expected model name")
    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    try:
        payload = fetch_json(f"{base_url}/api/tags")
    except HTTPError as exc:
        print(f"Ollama responded with HTTP {exc.code}: {exc.reason}", file=sys.stderr)
        return 2
    except URLError as exc:
        print(f"Ollama is unreachable at {base_url}: {exc.reason}", file=sys.stderr)
        return 2
    except TimeoutError:
        print(f"Ollama timed out at {base_url}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"Ollama returned invalid JSON: {exc}", file=sys.stderr)
        return 2

    models = [item.get("name", "") for item in payload.get("models", [])]
    print(f"Ollama reachable: {base_url}")
    if models:
        print("Models:")
        for name in models:
            marker = "*" if name == args.model else "-"
            print(f"  {marker} {name}")
    else:
        print("No models installed.")

    if not has_model(models, args.model):
        print(f"Expected model not found: {args.model}", file=sys.stderr)
        return 1

    print(f"Expected model found: {args.model}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
