# Smoke Publish Gate

This runbook defines the approval gate for the first real GHCR publish. It does
not grant approval by itself. The workflow is manual-only, defaults to
`dry_run: true`, and requires both repository configuration and the exact
approval phrase before any `dry_run: false` publish can run.

## Scope

- First image: `keystone`.
- Profile: `core`.
- Release: `2025.1`.
- Distro: `rocky`.
- Distro version: `9`.
- Architectures: `amd64` and `arm64`.
- Deploy tag: `2025.1-rocky-9`.
- Per-arch tags: `2025.1-rocky-9-amd64` and `2025.1-rocky-9-arm64`.

`keystone` is the smoke candidate because it is a core control-plane service and
has a narrower dependency surface than the Nova and Neutron image families.

## Required Approval

Do not run a real publish unless a human gives this exact approval in the PR,
issue, or Conductor thread:

```text
I approve GHCR smoke publish for keystone 2025.1-rocky-9 from supergate-jhbyun/kolla-image-build.
```

Approval is required in addition to any repository variable or workflow input.
`ALLOW_GHCR_PUBLISH=true` by itself is not approval.

## Preflight

Before real publish is implemented or run:

- `main` is up to date and validate CI is green.
- `python3 scripts/validate-config.py` passes.
- `python3 scripts/plan-publish.py --profile core --image keystone --release 2025.1 --distro rocky --distro-version 9 --dry-run` produces the expected `keystone` plan.
- Runner has Docker Engine, Docker Buildx, BuildKit, Python 3, network access
  for `pip`, and enough disk for the smoke build.
- Workflow installs `kolla==20.4.0` and the Python Docker SDK before running
  `kolla-build`.
- Workflow permissions include `contents: read` and `packages: write`.
- GHCR publish uses the repository `GITHUB_TOKEN`; no PAT is required for the
  first workflow-based publish.
- The intended GHCR package visibility is confirmed before anonymous pull is
  treated as a requirement.
- No site-local secret, kubeconfig, private CA, registry credential, OpenStack
  credential, or environment-specific config is added to the image build.

Run the safe workflow path first:

```bash
gh workflow run publish.yml \
  --ref main \
  -f release=2025.1 \
  -f distro=rocky \
  -f distro_version=9 \
  -f profile=core \
  -f image=keystone \
  -f dry_run=true
```

The dry-run output must include these refs:

```text
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-amd64
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-arm64
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9
```

## Publish Sequence

After explicit approval and preflight confirmation, the first smoke publish
executes only the `keystone` entries from the plan:

1. Render the publish plan plus parent and service-group matrices.
2. Build and push `base`, `openstack-base`, and `keystone-base` once on each
   native architecture runner.
3. Pre-pull those parent tags and build the `keystone` leaf with
   `--skip-existing` on each architecture runner.
4. Inspect each per-architecture ref in its build job.
5. Create and inspect the architecture-neutral manifest in the finalize job.
6. Validate and upload the manifest metadata and digest summary artifacts.

The manual workflow run must include:

```bash
gh workflow run publish.yml \
  --ref main \
  -f release=2025.1 \
  -f distro=rocky \
  -f distro_version=9 \
  -f profile=core \
  -f image=keystone \
  -f dry_run=false \
  -f approval='I approve GHCR smoke publish for keystone 2025.1-rocky-9 from supergate-jhbyun/kolla-image-build.'
```

## Verification

Record the output of:

```bash
docker buildx imagetools inspect \
  ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-amd64
docker buildx imagetools inspect \
  ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-arm64
docker buildx imagetools inspect \
  ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9
```

If the package is intended to be public, verify anonymous pull from a clean
Docker auth state:

```bash
docker logout ghcr.io
docker pull --platform linux/amd64 \
  ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9
docker pull --platform linux/arm64 \
  ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9
```

The smoke result must include:

- amd64 image ref and digest;
- arm64 image ref and digest;
- multi-arch deploy ref and digest;
- GHCR visibility setting;
- anonymous pull result, if public pull is required.

The workflow artifact is named from the selected image and tag inputs, for
example `kolla-publish-keystone-2025.1-rocky-9`. Inspect:

- `artifacts/plan/publish-plan.json` for the exact command plan;
- `artifacts/logs/*-build.log` for Kolla build and push logs;
- `artifacts/logs/*-inspect.log` for per-arch and manifest inspections;
- `artifacts/arch/*-*.json` for per-architecture refs assembled by matrix
  jobs;
- `artifacts/manifests/keystone-2025.1-rocky-9.json` for Docker manifest
  metadata;
- `artifacts/manifests/smoke-publish-summary.json` for the digest summary
  assembled by the workflow;
- `artifacts/publish-summary-2025.1-rocky-9.json` for the publish summary
  shape consumed by `scripts/generate-lock.py`.

This first smoke publish is not a staging or production promotion by itself. A
promotable lock must be generated from a full `core` profile publish summary
with `scripts/generate-lock.py` and validated with `scripts/validate-lock.py`.

## Stop Conditions

Stop before publish if:

- the exact approval text is missing;
- `ALLOW_GHCR_PUBLISH=true` is not set for the repository;
- workflow inputs are anything other than `core/keystone 2025.1-rocky-9`;
- runner tooling is missing or unverified;
- dry-run output differs from the expected refs;
- GHCR visibility or package ownership is unclear;
- an existing GHCR package in the target namespace is not linked to this
  repository;
- any secret or site-local config would be baked into the image.

## Human Inputs Still Required

- Explicit approval text for the smoke publish.
- Confirmation of GHCR package visibility policy.
- Confirmation that GitHub-hosted or self-hosted runners have enough disk and
  cross-platform build support.
- Repository variable `ALLOW_GHCR_PUBLISH=true` when the real publish
  implementation exists.

No additional secret is required for the first workflow-based publish if the
repository `GITHUB_TOKEN` can create and link the GHCR package. A future private
base registry or mirror would require separate credentials and a new review.
