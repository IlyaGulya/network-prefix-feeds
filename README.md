# network-prefix-feeds

Generic network prefix feed generator for policy routing and egress control.

This repository is intentionally separate from any single consumer. Today it
generates GitHub IPv4 prefix feeds. Later it can grow additional providers
without changing the consumer-side contract.

## Current provider

- `GitHub`

Source:

- `https://api.github.com/meta`

## Generated assets

The workflow publishes assets into the `latest` GitHub release.

Current GitHub assets:

- `github-all-ipv4.txt`
- `github-api-ipv4.txt`
- `github-actions-ipv4.txt`
- `github-actions-macos-ipv4.txt`
- `github-codespaces-ipv4.txt`
- `github-copilot-ipv4.txt`
- `github-git-ipv4.txt`
- `github-github-enterprise-importer-ipv4.txt`
- `github-hooks-ipv4.txt`
- `github-importer-ipv4.txt`
- `github-packages-ipv4.txt`
- `github-pages-ipv4.txt`
- `github-web-ipv4.txt`
- `github-manifest.json`

Format:

- plain text feeds contain one IPv4 CIDR per line
- `github-manifest.json` contains metadata and counts

## Why this exists

RouterOS is much happier consuming a simple line-based feed than parsing a
large JSON payload from a third-party API directly on-device.

That gives us:

- simpler MikroTik scripts
- cleaner debugging
- provider-specific normalization in one place
- room to add more services later without changing the feed contract

## Consumer example

For MikroTik/OpenTofu consumers, use the public release asset URL:

```text
https://github.com/<owner>/network-prefix-feeds/releases/latest/download/github-all-ipv4.txt
```

If you want to route only specific GitHub surfaces later, use a more specific
asset such as `github-git-ipv4.txt`, `github-packages-ipv4.txt` or
`github-actions-ipv4.txt`.

## Local build

```bash
cd /Users/ilyagulya/Projects/My/network-prefix-feeds
python3 scripts/build_feeds.py
```

Generated files appear under `dist/`.

## Release workflow

The workflow:

1. fetches GitHub Meta API
2. generates normalized IPv4 feeds
3. creates or updates the `latest` release
4. uploads the current assets with overwrite enabled

## Future expansion

This repo name is intentionally generic. Later we can add:

- other SaaS providers
- regionalized feeds
- service-specific feeds
- IPv6 feeds
- curated allowlists or denylists
