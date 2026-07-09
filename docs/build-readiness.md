# Real Build Readiness

This document defines what must be true before replacing the manual publish
workflow guard with real Kolla image build and GHCR publish steps.

## Runner and Tooling Requirements

- Linux runner with enough disk for Kolla base layers, service image layers, and
  build cache.
- Python 3 with network access to install the `kolla` package.
- Docker Engine with BuildKit enabled.
- Docker Buildx plugin installed.
- A buildx builder capable of the selected platform builds.
- GHCR authentication through `GITHUB_TOKEN`.
- Workflow permissions set to `contents: read` and `packages: write`.

Kolla supports Docker and Podman. The first publish path uses Docker because the
manifest plan uses `docker buildx imagetools`.

The GitHub workflow installs `kolla==20.4.0` and the Python Docker SDK for the
2025.1 Epoxy smoke publish, then prepares QEMU plus a Buildx builder before
running `dry_run: false`.

## Command Plan Shape

`scripts/plan-publish.py` emits executable command arrays. Workflow code should
execute those arrays rather than reassembling shell strings.

For the first smoke publish, render only `keystone`:

```bash
python3 scripts/plan-publish.py \
  --profile core \
  --image keystone \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  --dry-run
```

Example amd64 build command:

```bash
kolla-build \
  --engine docker \
  --base rocky \
  --base-tag 9 \
  --base-arch x86_64 \
  --platform linux/amd64 \
  --openstack-release 2025.1 \
  --registry ghcr.io \
  --namespace supergate-jhbyun/kolla-image-build \
  --tag 2025.1-rocky-9-amd64 \
  --push \
  '^keystone$'
```

The arm64 command uses `--base-arch aarch64` and `--platform linux/arm64`.

Do not create the architecture-neutral deploy tag until both per-architecture
refs exist in GHCR.

## Manifest Plan

Create the multi-arch manifest only after both architecture-specific refs have
been pushed:

```bash
docker buildx imagetools create \
  --tag ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9 \
  --metadata-file artifacts/manifests/keystone-2025.1-rocky-9.json \
  ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-amd64 \
  ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-arm64
```

Then inspect the deploy tag:

```bash
docker buildx imagetools inspect \
  ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9
```

The workflow artifact should include:

- image name;
- deploy tag;
- amd64 ref and digest;
- arm64 ref and digest;
- multi-arch ref and digest;
- `docker buildx imagetools create --metadata-file` output.
- build and inspect logs for each per-architecture ref.

For a full profile publish, write the digest set to:

```text
artifacts/publish-summary-2025.1-rocky-9.json
artifacts/publish-summary-2025.1-ubuntu-24.04.json
```

Then render the Kolla-Ansible lock:

```bash
python3 scripts/generate-lock.py \
  --publish-summary artifacts/publish-summary-2025.1-rocky-9.json \
  --profile core \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  --output artifacts/kolla-ansible-image-lock-2025.1-rocky-9.yml
```

Validate stg/prod locks before using them:

```bash
python3 scripts/validate-lock.py \
  --environment stg \
  --profile core \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  artifacts/kolla-ansible-image-lock-2025.1-rocky-9.yml
```

Staging and production validation rejects tag-only refs. Production promotion
uses the exact lock file that passed staging smoke validation.

## GHCR Checklist

- Repository is published from the intended organization-owned namespace.
- Package visibility policy allows the intended anonymous public pulls.
- Workflow has `packages: write`.
- First publish links the package to this repository.
- Anonymous pull works after visibility is configured.
- No private CA, kubeconfig, registry credential, OpenStack credential, or
  site-local config is baked into the image.

## First Build Candidate

Use `keystone` from the `core` profile as the first smoke publish candidate. It
is a control-plane service with a narrow dependency surface compared with the
larger Nova and Neutron image families.

Do not publish until a human explicitly approves smoke publish and confirms GHCR
visibility policy.

The exact approval gate, dry-run checks, publish checks, and stop conditions are
defined in [smoke-publish-gate.md](smoke-publish-gate.md).

## References

- Kolla image building:
  <https://docs.openstack.org/kolla/latest/admin/image-building.html>
- Docker Buildx imagetools:
  <https://docs.docker.com/reference/cli/docker/buildx/imagetools/create/>
- GitHub Container registry:
  <https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry>
- GitHub package visibility:
  <https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages>
