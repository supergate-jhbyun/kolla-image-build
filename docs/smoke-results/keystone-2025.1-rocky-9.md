# Keystone 2025.1 Rocky 9 Smoke Results

Date: 2026-07-09

## Dry Run

Workflow run:
<https://github.com/supergate-jhbyun/kolla-image-build/actions/runs/28994203150>

Result: success

Validated dry-run refs:

```text
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-amd64
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-arm64
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9
```

Artifact inspected:

```text
kolla-publish-keystone-2025.1-rocky-9/plan/publish-plan.json
```

## GHCR Smoke Publish

Workflow run:
<https://github.com/supergate-jhbyun/kolla-image-build/actions/runs/28996674086>

Result: success

Published refs:

```text
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-amd64
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-arm64
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9
```

Manifest digest:

```text
sha256:faf9549e70edbb012c3b7289fa48d84cff803da56055a8a1ac785c6288433a65
```

Architecture digests:

```text
linux/amd64 sha256:ea8a8204159496c9dca97b0e147dd2847fffea133e5a56610f3344a74be8da75
linux/arm64 sha256:c1af7cd1120dfb471ce4bb240896a78e775557c921e80398e240d8ea060a33bd
```

Artifacts inspected:

```text
kolla-publish-keystone-2025.1-rocky-9/manifests/keystone-2025.1-rocky-9.json
kolla-publish-keystone-2025.1-rocky-9/manifests/smoke-publish-summary.json
kolla-publish-keystone-2025.1-rocky-9/publish-summary-2025.1-rocky-9.json
```

GHCR visibility:

```text
Public package page exposes keystone:2025.1-rocky-9 with Installation OS / Arch 2.
Anonymous docker buildx imagetools inspect succeeded for amd64, arm64, and deploy refs.
```

Anonymous pull verification:

```text
docker pull --platform linux/amd64 ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9
docker pull --platform linux/arm64 ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9
```

Both pulls succeeded using a Docker config without GHCR credentials.
