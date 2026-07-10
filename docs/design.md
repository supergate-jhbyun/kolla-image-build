# kolla-image-build Design

## Goals

This repository centralizes the build configuration for Kolla images that must
be reused across development, staging, and production-like OpenStack
environments.

The initial scaffold does not build or publish images. It creates the smallest
safe base for validating naming, supported matrix entries, and future CI
automation.

## Naming Policy

The build and publish interface is an architecture-neutral tag:

```text
ghcr.io/<owner>/kolla-image-build/<image>:<release>-<distro>-<distro_version>
```

Examples:

```text
ghcr.io/supergate-jhbyun/kolla-image-build/nova-compute:2025.1-rocky-9
ghcr.io/supergate-jhbyun/kolla-image-build/nova-compute:2025.1-ubuntu-24.04
```

Architecture-specific tags are only for debugging and reproducibility:

```text
<release>-<distro>-<distro_version>-amd64
<release>-<distro>-<distro_version>-arm64
```

All environments use generated Kolla-Ansible `*_image_full` overrides with the
architecture-neutral manifest digest attached:

```text
ghcr.io/supergate-jhbyun/kolla-image-build/<image>:2025.1-rocky-9@sha256:<manifest-digest>
```

The lock generator maps concrete Kolla image names to actual Kolla-Ansible
variables such as `glance_api_image_full`, `nova_api_image_full`, and
`nova_compute_image_full`.

## Multi-Architecture Manifest Policy

Publish workflows should produce this sequence:

```text
render parent and service-group matrices
build shared parents once per native architecture
pre-pull parent tags in fresh service-group runners
build service groups in parallel per native architecture
push and inspect per-arch leaf tags
create architecture-neutral manifest tag
inspect final manifest
record manifest digests and generate the full-profile lock
```

The `core` smoke profile and `deployment` runtime profile own explicit build
groups. Shared `base`, `openstack-base`, and service base images are built
before leaf jobs. Leaf jobs use
`--skip-existing` only after pre-pulling those exact parent tags; they do not
use `--skip-parents`, because a deployable Kolla image such as `nova-compute`
can itself have children in the complete Kolla dependency graph.

The workflow serializes every profile publisher for the same release, distro,
and version because core and deployment profiles share architecture tags.

Promotion between environments uses the final manifest digest, not a mutable
environment tag such as `dev`, `staging`, or `prod`.

## Environment Lock Policy

Expected lock paths are:

```text
locks/dev/core-2025.1-rocky-9.yml
locks/dev/core-2025.1-ubuntu-24.04.yml
locks/stg/core-2025.1-rocky-9.yml
locks/stg/core-2025.1-ubuntu-24.04.yml
locks/prod/core-2025.1-rocky-9.yml
locks/prod/core-2025.1-ubuntu-24.04.yml
locks/dev/deployment-2025.1-rocky-9.yml
locks/stg/deployment-2025.1-rocky-9.yml
locks/prod/deployment-2025.1-rocky-9.yml
```

Dev, staging, and production validation fails if any ref is tag-only or if a
Rocky and Ubuntu tag are mixed in the same lock. Deployment parents never
appear in an environment lock; only enabled Kolla leaf variables are pinned.

Production promotion is a copy of the staging-verified digest set for the full
`profile + release + distro-version` tuple. Rollback is a restore of a previous
production lock file, not a rebuild or tag reinterpretation.

## Namespace and Repository Transfer Policy

A personal repository is acceptable for source and workflow proof of concept
work. Images published from a personal namespace must remain demo-only.

Do not assume GHCR packages move cleanly when the repository is transferred to
an organization. GitHub Container Registry packages use granular permissions,
and repository transfer can remove package links and workflow access.

Organization environments should republish images from the final organization
repository and namespace:

```text
ghcr.io/<org>/kolla-image-build/<image>:2025.1-rocky-9
```

## Public Image Constraints

Public images must not contain private registry credentials, site-local CA
material, kubeconfigs, OpenStack credentials, or internal-only configuration.
Those values belong in deployment-time configuration, not in the image build.

## References

- Kolla image building: https://docs.openstack.org/kolla/latest/admin/image-building.html
- GitHub Packages permissions: https://docs.github.com/en/packages/learn-github-packages/about-permissions-for-github-packages
- Docker manifest tooling: https://docs.docker.com/reference/cli/docker/buildx/imagetools/create/
