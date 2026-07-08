# kolla-image-build

This repository defines the first-stage scaffold for building Kolla container
images for multiple OpenStack lab and production-like environments.

The v1 scope is intentionally narrow:

- document the image naming and promotion strategy;
- define a small build matrix for Rocky, Ubuntu, amd64, and arm64;
- validate the repository configuration in CI;
- do not publish to GHCR yet;
- do not build real Kolla images yet.

## Image Strategy

Kolla-Ansible should consume an architecture-neutral deployment tag. The
registry decides which platform image to pull through a multi-architecture
manifest.

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

Per-architecture tags are debug and reproduction artifacts, not the primary
Kolla-Ansible deployment interface:

```text
2025.1-rocky-9-amd64
2025.1-rocky-9-arm64
2025.1-ubuntu-24.04-amd64
2025.1-ubuntu-24.04-arm64
```

## Kolla-Ansible Consumption

For deployment, configure Kolla-Ansible with the GHCR namespace and the
architecture-neutral tag:

```yaml
docker_registry: "ghcr.io"
docker_namespace: "supergate-jhbyun/kolla-image-build"
openstack_tag: "2025.1-rocky-9"
```

The owner is configurable. A personal namespace can be used for a proof of
concept, but organization-owned environments should publish from the final
organization namespace before any shared dev, staging, or production use.

## Repository Layout

```text
config/build-matrix.json      Supported release, distro, and arch matrix
config/profiles/core.json     Initial Kolla image profile for smoke validation
scripts/validate-config.py    Repository configuration validator
docs/design.md                Design notes and promotion policy
```

## Validation

Run local validation with:

```bash
python3 -m json.tool config/build-matrix.json
python3 -m json.tool config/profiles/core.json
python3 scripts/validate-config.py
python3 scripts/plan-publish.py --profile core --release 2025.1 --distro rocky --distro-version 9 --dry-run
python3 -m unittest discover -s tests -v
```

CI runs the same checks on push and pull request.

## Manual Publish Workflow

The publish workflow is manual-only and safe by default:

```text
.github/workflows/publish.yml
```

It accepts release, distro, distro version, profile, and `dry_run` inputs. The
default `dry_run: true` path renders the same publish plan as the local planner
and does not build or push images.

The `dry_run: false` path is intentionally guarded. It requires the repository
variable `ALLOW_GHCR_PUBLISH=true` and still fails because real GHCR publish is
not implemented in this scaffold. A later implementation PR must replace that
guard with the actual build, push, manifest, and digest-recording steps.

## Next Steps

After the scaffold is validated, add a workflow-dispatched build pipeline that:

1. builds per-architecture Kolla images;
2. pushes architecture-specific debug tags;
3. creates an architecture-neutral multi-arch manifest tag;
4. records the final manifest digest for dev, staging, and production
   promotion.
