# network-prefix-feeds

Generic network prefix feed generator for policy routing and egress control.

This repository is intentionally separate from any single consumer. Today it
generates GitHub IPv4 prefix feeds. Later it can grow additional providers
without changing the consumer-side contract.

## Current provider

- `GitHub`

Source:

- `https://api.github.com/meta`

## Generated feeds

The workflow regenerates tracked files under [`feeds/`](/Users/ilyagulya/Projects/My/network-prefix-feeds/feeds) and commits them back to `main`.
Netlify builds the same feeds into a static `public/` site so routers can fetch them without depending on GitHub-hosted asset delivery.

Current GitHub assets:

- `github-all-ipv4.txt`
- `github-core-ipv4.txt`
- `routeros-github-all.rsc`
- `routeros-github-core.rsc`
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

Preferred delivery target for routers is the Netlify site:

```text
https://<site>.netlify.app/feeds/routeros-github-core.rsc
```

Why:

- it avoids GitHub release redirects
- it avoids brittle `raw.githubusercontent.com` fetches from constrained devices
- it gives a stable static site dedicated to feed delivery

If you want to route only specific GitHub surfaces later, use a more specific
asset such as `github-core-ipv4.txt`, `github-git-ipv4.txt`,
`github-packages-ipv4.txt` or `github-actions-ipv4.txt`.

Recommended default for routers:

- `github-core-ipv4.txt`
- for MikroTik specifically: `routeros-github-core.rsc`

Why:

- it covers the normal user-facing GitHub surfaces: `web`, `api`, `git`, `pages`, `packages`, `hooks`
- it avoids the very large `github-all-ipv4.txt`, which pulls in categories like `actions` and is less friendly to constrained devices such as RouterOS
- the `.rsc` variant lets RouterOS import ready-made address-list commands instead of parsing text line-by-line on-device

## Local build

```bash
cd /Users/ilyagulya/Projects/My/network-prefix-feeds
python3 scripts/build_feeds.py
python3 scripts/build_site.py
```

Generated files appear under `feeds/` and `public/`.

## Release workflow

The workflow:

1. fetches GitHub Meta API
2. generates normalized IPv4 feeds
3. commits refreshed files into `feeds/` on `main`
4. updates the `latest` release with the same files

## Netlify

- `netlify.toml` builds `public/` with `python3 scripts/build_site.py`
- `public/feeds/` mirrors the generated feed assets for static hosting
- `public/index.html` provides a simple asset index page

## Future expansion

This repo name is intentionally generic. Later we can add:

- other SaaS providers
- regionalized feeds
- service-specific feeds
- IPv6 feeds
- curated allowlists or denylists
