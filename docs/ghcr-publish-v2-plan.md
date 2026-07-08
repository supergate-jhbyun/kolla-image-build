# GHCR Publish v2 Plan

## Goal

Add an explicit, manually triggered image publish pipeline after the v1 scaffold
is merged. The v2 pipeline should build Kolla images per architecture, publish
debug tags, create architecture-neutral multi-arch manifest tags, and record the
final manifest digest for environment promotion.

## Non-Goals

- Do not publish images from the v1 scaffold PR.
- Do not add automatic publish on every push.
- Do not bake site-local secrets, registry credentials, CA material,
  kubeconfigs, or OpenStack credentials into public images.
- Do not use mutable environment tags such as `dev`, `staging`, or `prod` as the
  promotion source of truth.

## Proposed Workflow

Use a new workflow-dispatched pipeline, for example:

```text
.github/workflows/publish.yml
```

Inputs:

```text
release: 2025.1
distro: rocky | ubuntu
distro_version: 9 | 24.04
profile: core
dry_run: true | false
```

Required permissions:

```yaml
permissions:
  contents: read
  packages: write
```

The workflow should run only through `workflow_dispatch` until the image set is
proven repeatable.

## Publish Sequence

For each selected image and architecture:

```text
validate matrix and profile
build amd64 image
push <release>-<distro>-<distro_version>-amd64
build arm64 image
push <release>-<distro>-<distro_version>-arm64
inspect both per-arch image refs
create <release>-<distro>-<distro_version> multi-arch manifest
inspect final manifest
write manifest digest to an artifact
```

The deploy tag must remain architecture-neutral:

```text
ghcr.io/<owner>/kolla-image-build/<image>:2025.1-rocky-9
```

The architecture tags remain debug and reproduction artifacts:

```text
ghcr.io/<owner>/kolla-image-build/<image>:2025.1-rocky-9-amd64
ghcr.io/<owner>/kolla-image-build/<image>:2025.1-rocky-9-arm64
```

## Implementation Tasks

1. Add a dry-run command generator that turns `config/build-matrix.json` and
   `config/profiles/<name>.json` into the exact `kolla-build` and manifest
   commands without executing them.
2. Add tests for the generated tag names and command plan.
3. Add `publish.yml` with `workflow_dispatch`, `contents: read`, and
   `packages: write`.
4. Run the workflow in `dry_run: true` mode and verify command output only.
5. Enable `dry_run: false` for one low-risk image from the `core` profile.
6. Verify anonymous pull for public GHCR packages after package visibility is
   set correctly.
7. Promote by recording the final multi-arch manifest digest, not by relying on
   a mutable environment tag.

## Acceptance Criteria

- `scripts/validate-config.py` still passes.
- `actionlint` passes for all workflows.
- Publish workflow is manual-only.
- No GHCR package is pushed unless `dry_run` is explicitly false.
- Final artifact includes image name, deploy tag, amd64 digest, arm64 digest,
  and multi-arch manifest digest.

## Risks

- GitHub repository transfer does not automatically make personal GHCR packages
  organization-scoped. Organization-owned images should be republished from the
  final organization namespace.
- Newly published GHCR packages may require visibility and repository access
  settings before anonymous pull works.
- arm64 Kolla builds can expose base image or package availability gaps that are
  not visible in amd64-only validation.
