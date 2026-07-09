# kolla-image-build

This repository defines the build and promotion scaffold for Kolla container
images used by development, staging, and production-like OpenStack
environments.

The current scope is intentionally narrow:

- document the image naming and promotion strategy;
- define a small build matrix for Rocky, Ubuntu, amd64, and arm64;
- keep the production build path aligned with upstream `kolla-build`;
- render dry-run publish plans without executing them;
- generate Kolla-Ansible image locks from publish digest summaries;
- validate repository configuration and lock policy in CI.

## Image Strategy

Kolla-Ansible dev environments may consume an architecture-neutral deployment
tag. The registry decides which platform image to pull through a
multi-architecture manifest.

Canonical deployment tag:

```text
ghcr.io/<owner>/kolla-image-build/<image>:2025.1-rocky-9
```

Example deployment references:

```text
ghcr.io/supergate-jhbyun/kolla-image-build/nova-compute:2025.1-rocky-9
ghcr.io/supergate-jhbyun/kolla-image-build/neutron-server:2025.1-rocky-9
ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-ubuntu-24.04
```

Per-architecture tags are debug and reproduction artifacts, not the
staging/production deployment interface:

```text
2025.1-rocky-9-amd64
2025.1-rocky-9-arm64
2025.1-ubuntu-24.04-amd64
2025.1-ubuntu-24.04-arm64
```

## Kolla-Ansible Consumption

For fast dev iteration, configure Kolla-Ansible with the GHCR namespace and the
architecture-neutral tag:

```yaml
docker_registry: "ghcr.io"
docker_namespace: "supergate-jhbyun/kolla-image-build"
openstack_tag: "2025.1-rocky-9"
```

For staging and production, do not rely on `openstack_tag` alone. Generate and
include a digest-pinned `*_image_full` lock file:

```yaml
keystone_image_full: "ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9@sha256:<manifest-digest>"
glance_api_image_full: "ghcr.io/supergate-jhbyun/kolla-image-build/glance-api:2025.1-rocky-9@sha256:<manifest-digest>"
nova_compute_image_full: "ghcr.io/supergate-jhbyun/kolla-image-build/nova-compute:2025.1-rocky-9@sha256:<manifest-digest>"
```

The `core` profile is defined as concrete Kolla image names plus their
Kolla-Ansible `*_image_full` variables, not logical service labels.

The owner is configurable. A personal namespace can be used for a proof of
concept, but organization-owned environments should publish from the final
organization namespace before any shared dev, staging, or production use.

## Repository Layout

```text
config/build-matrix.json      Supported release, distro, and arch matrix
config/profiles/core.json     Kolla image to Kolla-Ansible variable mapping
scripts/validate-config.py    Repository configuration validator
scripts/plan-publish.py       Dry-run kolla-build and manifest command planner
scripts/generate-lock.py      Digest summary to Kolla-Ansible lock renderer
scripts/validate-lock.py      Dev/stg/prod lock policy validator
locks/                        Environment lock policy and future lock files
docs/design.md                Design notes and promotion policy
docs/build-readiness.md       Real build command and runner readiness notes
docs/smoke-publish-gate.md    Approval gate and runbook for first publish
```

## Validation

Run local validation with:

```bash
python3 -m json.tool config/build-matrix.json
python3 -m json.tool config/profiles/core.json
python3 scripts/validate-config.py
python3 scripts/plan-publish.py --profile core --release 2025.1 --distro rocky --distro-version 9 --dry-run
python3 scripts/plan-publish.py --profile core --image keystone --release 2025.1 --distro rocky --distro-version 9 --dry-run
python3 -m unittest discover -s tests -v
```

CI runs the same checks on push and pull request.

## Manual Publish Workflow

The publish workflow is manual-only and safe by default:

```text
.github/workflows/publish.yml
```

It accepts release, distro, distro version, profile, image, `dry_run`, and
approval inputs. The default `dry_run: true` path renders the same publish plan
as the local planner, uploads that plan as a workflow artifact, and does not
build or push images.

Run the dry-run workflow with:

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

The `dry_run: false` smoke path is intentionally guarded. It requires the
repository variable `ALLOW_GHCR_PUBLISH=true`, the exact approval phrase
documented in [docs/smoke-publish-gate.md](docs/smoke-publish-gate.md), and the
first smoke scope `core/keystone 2025.1-rocky-9`. If those gates pass, the
workflow runs the planned per-architecture Kolla build commands, creates the
multi-arch manifest, inspects the result, and uploads logs plus manifest
metadata as artifacts.

For a full profile publish, convert the publish summary into a lock:

```bash
python3 scripts/generate-lock.py \
  --publish-summary artifacts/publish-summary-2025.1-rocky-9.json \
  --profile core \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  --output artifacts/kolla-ansible-image-lock-2025.1-rocky-9.yml

python3 scripts/validate-lock.py \
  --environment stg \
  --profile core \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  artifacts/kolla-ansible-image-lock-2025.1-rocky-9.yml
```

Expected promoted lock paths are documented in [locks/README.md](locks/README.md).

See [docs/build-readiness.md](docs/build-readiness.md) for the Kolla build
command plan, Docker manifest commands, runner requirements, and GHCR preflight
checklist.

See [docs/smoke-publish-gate.md](docs/smoke-publish-gate.md) for the explicit
human approval gate and first-image smoke publish runbook. Until that approval
is given and runner/GHCR preflight is confirmed, use dry-run only.

## Next Steps

Before the first real smoke publish:

1. confirm GHCR visibility policy and package ownership;
2. confirm the selected runner has Docker, Buildx, BuildKit, Python 3, Kolla,
   enough disk, and cross-platform build support;
3. set `ALLOW_GHCR_PUBLISH=true`;
4. provide the exact approval phrase from
   [docs/smoke-publish-gate.md](docs/smoke-publish-gate.md);
5. run the manual workflow for `keystone` only;
6. review the digest artifacts before expanding beyond the smoke image.
