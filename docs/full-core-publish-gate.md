# Full-Core Publish Gate

This runbook covers the one-time approved GHCR publish for the complete Rocky
9 `core` profile. It does not authorize another release, distro, profile, or a
production lock promotion.

## Approved Scope

```text
profile: core
image: all
release: 2025.1
distro: rocky
distro_version: 9
architectures: amd64, arm64
leaf images: 21
shared parents: 8
service groups: 7
```

The exact approval phrase is:

```text
I approve GHCR full-core publish for core 2025.1-rocky-9 (21 images, amd64/arm64) from supergate-jhbyun/kolla-image-build.
```

Real full-core publish also requires the temporary repository variable
`ALLOW_GHCR_FULL_CORE_PUBLISH=true`. The existing
`ALLOW_GHCR_PUBLISH=true` variable authorizes only the keystone smoke scope.

## Capacity Model

The workflow renders two native parent jobs, one per architecture. After both
complete, it renders fourteen service-group jobs: seven groups times two
architectures. The leaf matrix allows at most eight jobs at once. Each Kolla
invocation uses four build threads and one push thread.

The parent jobs build these shared images once per architecture:

```text
base
openstack-base
keystone-base
glance-base
placement-base
nova-base
neutron-base
heat-base
```

Service jobs pre-pull their exact parent tags and use `--skip-existing`, so
they must report those parents as skipped rather than rebuilt. Native runner
mapping is `ubuntu-24.04` for amd64 and `ubuntu-24.04-arm` for arm64. QEMU is
not part of this flow.

## Preflight

Run all local checks before enabling the temporary variable:

```bash
python3 -m json.tool config/build-matrix.json >/dev/null
python3 -m json.tool config/profiles/core.json >/dev/null
python3 scripts/validate-config.py
python3 scripts/plan-publish.py --profile core --release 2025.1 --distro rocky --distro-version 9 --dry-run >/tmp/kolla-plan-rocky.json
python3 scripts/plan-publish.py --profile core --release 2025.1 --distro ubuntu --distro-version 24.04 --dry-run >/tmp/kolla-plan-ubuntu.json
python3 -m unittest discover -s tests -v
actionlint
git diff --check
```

Confirm the active GitHub account before any write:

```bash
gh auth switch -h github.com -u supergate-jhbyun
gh auth status --active
```

## Dry Run

```bash
gh workflow run publish.yml \
  --ref supergate-jhbyun/kolla-ghcr-lock-ops \
  -f release=2025.1 \
  -f distro=rocky \
  -f distro_version=9 \
  -f profile=core \
  -f image=all \
  -f dry_run=true
```

The downloaded plan must contain 21 leaf images, 8 unique parents, 7 service
groups, 2 parent matrix entries, 14 leaf matrix entries, 42 architecture refs,
and 21 deploy refs. The run must finish with no annotations.

## Real Publish

Enable the one-time gate only after the dry run passes:

```bash
gh variable set ALLOW_GHCR_FULL_CORE_PUBLISH \
  --body true \
  --repo supergate-jhbyun/kolla-image-build
```

Dispatch the approved scope:

```bash
gh workflow run publish.yml \
  --ref supergate-jhbyun/kolla-ghcr-lock-ops \
  -f release=2025.1 \
  -f distro=rocky \
  -f distro_version=9 \
  -f profile=core \
  -f image=all \
  -f dry_run=false \
  -f approval='I approve GHCR full-core publish for core 2025.1-rocky-9 (21 images, amd64/arm64) from supergate-jhbyun/kolla-image-build.'
```

Watch the run to completion. Do not create or promote a lock if a parent,
service-group, finalize, summary validation, or lock validation step fails.

## Artifact Verification

The final artifact must contain:

```text
artifacts/publish-summary-2025.1-rocky-9.json
artifacts/kolla-ansible-image-lock-2025.1-rocky-9.yml
artifacts/arch/<image>-amd64.json
artifacts/arch/<image>-arm64.json
artifacts/manifests/<image>-2025.1-rocky-9.json
artifacts/manifests/<image>-publish-summary.json
```

Validate the full summary without `--allow-partial`:

```bash
python3 scripts/validate-publish-summary.py \
  --publish-summary artifacts/publish-summary-2025.1-rocky-9.json \
  --profile core \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9
```

Every image must have amd64 and arm64 architecture records and a `sha256:`
manifest digest. Every Kolla summary must have an empty `failed` list. Leaf
summaries must list the pre-pulled parent chain under `skipped`.

## Staging Lock

Copy or regenerate the validated workflow lock at:

```text
locks/stg/core-2025.1-rocky-9.yml
```

Then validate it:

```bash
python3 scripts/validate-lock.py \
  --environment stg \
  --profile core \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  locks/stg/core-2025.1-rocky-9.yml
```

Do not create or modify `locks/prod/core-2025.1-rocky-9.yml` until the exact
staging lock has passed an external staging deployment.

## Registry Verification

Inspect all 21 deploy tags and verify both platforms. If packages are intended
to be public, use a Docker configuration with no GHCR credentials for the
inspection and representative full image pulls. Package visibility is a
per-package external setting and must not be inferred from a successful
authenticated workflow push.

## Close The Gate

After the approved run completes, or immediately after a stopped/failed run,
reset the temporary variable:

```bash
gh variable set ALLOW_GHCR_FULL_CORE_PUBLISH \
  --body false \
  --repo supergate-jhbyun/kolla-image-build
```

Confirm its value before ending the operation.

## Stop And Rollback

Stop before or during publish when the plan shape changes, a runner lacks
capacity, a parent or leaf fails, digest metadata is missing, package ownership
is unclear, or any requested input is outside the approved scope.

Publishing updates mutable tags but does not promote a production deployment.
Rollback is performed by restoring the last staging-verified production lock
and validating it with `validate-lock.py` and `compare-locks.py`. Never rebuild
an old tag as a substitute for restoring the exact previous digest set.
