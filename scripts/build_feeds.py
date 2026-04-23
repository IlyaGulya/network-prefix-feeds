#!/usr/bin/env python3

from __future__ import annotations

import argparse
import ipaddress
import json
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "feeds"
GITHUB_META_URL = "https://api.github.com/meta"
GITHUB_CORE_CATEGORIES = (
    "web",
    "api",
    "git",
    "pages",
    "packages",
    "hooks",
)
ROUTEROS_GITHUB_LIST_NAME = "github-vpn-dst"
ROUTEROS_GITHUB_COMMENT = "GitOps side-router: GitHub prefix feed"


def fetch_json(url: str) -> dict[str, Any]:
    req_headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "network-prefix-feeds",
    }
    request = Request(url, headers=req_headers)
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_ipv4_prefixes(values: Iterable[str]) -> list[str]:
    seen: set[ipaddress.IPv4Network] = set()
    for value in values:
        if not isinstance(value, str) or "/" not in value:
            continue
        try:
            network = ipaddress.ip_network(value, strict=False)
        except ValueError:
            continue
        if isinstance(network, ipaddress.IPv4Network):
            seen.add(network)
    return [str(net) for net in sorted(seen, key=lambda n: (int(n.network_address), n.prefixlen))]


def write_lines(path: Path, lines: Iterable[str]) -> int:
    items = list(lines)
    path.write_text("".join(f"{line}\n" for line in items), encoding="utf-8")
    return len(items)


def format_routeros_address(prefix: str) -> str:
    network = ipaddress.ip_network(prefix, strict=False)
    if isinstance(network, ipaddress.IPv4Network) and network.prefixlen == network.max_prefixlen:
        return str(network.network_address)
    return str(network)


def write_routeros_rsc(path: Path, prefixes: Iterable[str]) -> int:
    items = list(prefixes)
    commands = [
        f'/ip firewall address-list remove [find where list="{ROUTEROS_GITHUB_LIST_NAME}" and comment="{ROUTEROS_GITHUB_COMMENT}"]'
    ]
    for prefix in items:
        address = format_routeros_address(prefix)
        commands.append(
            f':if ([:len [/ip firewall address-list find where list="{ROUTEROS_GITHUB_LIST_NAME}" and address="{address}"]] = 0) '
            f'do={{ /ip firewall address-list add list="{ROUTEROS_GITHUB_LIST_NAME}" address={address} comment="{ROUTEROS_GITHUB_COMMENT}" }}'
        )
    path.write_text("\n".join(commands) + "\n", encoding="utf-8")
    return len(items)


def github_feeds(meta: dict[str, Any]) -> dict[str, list[str]]:
    feeds: dict[str, list[str]] = {}
    for key, value in meta.items():
        if not isinstance(value, list):
            continue
        prefixes = normalize_ipv4_prefixes(value)
        if prefixes:
            feeds[key] = prefixes
    core_prefixes = normalize_ipv4_prefixes(
        prefix
        for category in GITHUB_CORE_CATEGORIES
        for prefix in feeds.get(category, [])
    )
    if core_prefixes:
        feeds["core"] = core_prefixes
    all_prefixes = normalize_ipv4_prefixes(prefix for prefixes in feeds.values() for prefix in prefixes)
    feeds["all"] = all_prefixes
    return feeds


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate normalized network prefix feeds.")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for generated feed files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    meta = fetch_json(GITHUB_META_URL)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    feeds = github_feeds(meta)

    assets: dict[str, dict[str, Any]] = {}
    for name, prefixes in feeds.items():
        filename = f"github-{name.replace('_', '-')}-ipv4.txt"
        path = output_dir / filename
        count = write_lines(path, prefixes)
        assets[filename] = {
            "provider": "github",
            "category": name,
            "family": "ipv4",
            "count": count,
        }

    for routeros_category in ("core", "all"):
        prefixes = feeds.get(routeros_category, [])
        if not prefixes:
            continue
        routeros_filename = f"routeros-github-{routeros_category}.rsc"
        routeros_path = output_dir / routeros_filename
        routeros_count = write_routeros_rsc(routeros_path, prefixes)
        assets[routeros_filename] = {
            "provider": "github",
            "category": routeros_category,
            "family": "routeros",
            "count": routeros_count,
        }

    manifest = {
        "generated_at_utc": generated_at,
        "sources": {
            "github_meta_api": GITHUB_META_URL,
        },
        "assets": assets,
    }
    (output_dir / "github-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    summary = ", ".join(f"{name}={meta['count']}" for name, meta in sorted(assets.items()))
    print(f"Generated feeds in {output_dir}: {summary}")


if __name__ == "__main__":
    main()
