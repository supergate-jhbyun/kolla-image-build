# Deployment Publish Gate

This gate authorizes only the complete Rocky 9 `deployment` profile for
OpenStack 2025.1. It does not authorize another release, distro, profile,
partial image selection, environment deployment, or lock promotion.

## Canonical Scope

```text
profile: deployment
image: all
release: 2025.1
distro: rocky
distro_version: 9
platforms: linux/amd64, linux/arm64
leaf images: 52
Kolla-Ansible variables: 54
shared parents: 13
service groups: 17
parent jobs: 2
leaf jobs: 34
architecture refs: 104
deploy refs: 52
```

The canonical approval phrase is:

```text
I approve GHCR deployment publish for deployment 2025.1-rocky-9 (52 images, amd64/arm64) from supergate-jhbyun/kolla-image-build.
```

A real publish also requires the temporary repository variable
`ALLOW_GHCR_DEPLOYMENT_PUBLISH=true`. Neither the keystone smoke variable nor
the full-core variable authorizes this scope.

## Closure Evidence

The leaf set was checked against the 69 running containers on web01 and a
read-only `kolla-ansible pull --check` using Kolla-Ansible commit
`d72865ea088215e06faba85bb79e67d031e46818`. The pull plan selected the same 52
unique images and changed no Docker image IDs. Kolla 20.4.0
`--list-dependencies` produced 13 parents:

```text
base
openstack-base
openvswitch-base
ovn-base
keystone-base
glance-base
placement-base
nova-base
neutron-base
heat-base
octavia-base
mariadb-base
prometheus-base
```

The disabled `mariadb-clustercheck` service and non-OVN Neutron agents are not
part of the current topology. `nova-conductor` and
`neutron-metadata-agent` each map both enabled Kolla role aliases to the same
manifest digest.

`control02` currently runs Rocky 10 Kolla tags while the other targets run
Rocky 9 tags. The deployment lock intentionally standardizes every target on
the same Rocky 9 manifest set, so the GHCR-only Horizon and Keystone canary is
mandatory before any destructive action.

## Dry Run

The dry run is allowed without enabling any publish variable:

```bash
gh workflow run publish.yml \
  --ref supergate-jhbyun/kolla-ghcr-lock-ops \
  -f release=2025.1 \
  -f distro=rocky \
  -f distro_version=9 \
  -f profile=deployment \
  -f image=all \
  -f dry_run=true
```

The downloaded plan must match every count in the canonical scope and have no
workflow annotations.

## Real Publish

Do not run these commands until the canonical approval phrase has been given:

```bash
gh variable set ALLOW_GHCR_DEPLOYMENT_PUBLISH \
  --body true \
  --repo supergate-jhbyun/kolla-image-build

gh workflow run publish.yml \
  --ref supergate-jhbyun/kolla-ghcr-lock-ops \
  -f release=2025.1 \
  -f distro=rocky \
  -f distro_version=9 \
  -f profile=deployment \
  -f image=all \
  -f dry_run=false \
  -f approval='I approve GHCR deployment publish for deployment 2025.1-rocky-9 (52 images, amd64/arm64) from supergate-jhbyun/kolla-image-build.'
```

Set the variable back to `false` immediately after success or failure. A
successful run must have no failed parent or leaf builds, exact native
architecture records, valid manifest digests, public packages, and anonymous
inspection for all 52 deploy refs.

## Dev Lock Boundary

Generate only this lock after a successful publish:

```text
locks/dev/deployment-2025.1-rocky-9.yml
```

Every one of its 54 variables must be digest pinned. Do not create staging or
production deployment locks until their preceding environment validation has
passed.
