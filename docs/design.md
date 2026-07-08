# kolla-image-build Design

## Goals

This repository centralizes the build configuration for Kolla images that must
be reused across development, staging, and production-like OpenStack
environments.

The initial scaffold does not build or publish images. It creates the smallest
safe base for validating naming, supported matrix entries, and future CI
automation.

## Naming Policy

The deployment interface is an architecture-neutral tag:

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

Kolla-Ansible should point to the architecture-neutral tag through
`openstack_tag`. This keeps deploy configuration aligned with the normal Kolla
registry and namespace model while letting the registry choose the correct
platform image.

## Multi-Architecture Manifest Policy

Future publish workflows should produce this sequence:

```text
build per-arch image
push per-arch debug tag
inspect pushed image
create architecture-neutral manifest tag
inspect final manifest
record manifest digest
```

Promotion between environments should use the final manifest digest, not a
mutable environment tag such as `dev`, `staging`, or `prod`.

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
