# Full Core 2025.1 Rocky 9 Publish Results

Date: 2026-07-10

## Scope

- Profile: `core`
- Selection: `all`
- Images: 21 leaf images
- Platforms: `linux/amd64`, `linux/arm64`
- Commit: `9f69b761bcdc5c51f4ed042d0fbcbdb7853e1235`
- Retries: none

No Ubuntu image was published. This result creates a staging lock only; it
does not record a staging deployment or a production promotion.

## Dry Run

Workflow run:
<https://github.com/supergate-jhbyun/kolla-image-build/actions/runs/29061656425>

Result: success

The downloaded plan contained 21 leaf images, 8 shared parents, 7 service
groups, 2 parent jobs, 14 leaf jobs, 42 architecture refs, and 21 deploy refs.
All workflow check runs reported zero annotations.

## GHCR Publish

Workflow run:
<https://github.com/supergate-jhbyun/kolla-image-build/actions/runs/29061723283>

Result: success in 21m09s

| Stage | amd64 | arm64 |
| --- | ---: | ---: |
| Shared parents | 8m58s | 8m28s |
| Identity | 4m40s | 5m51s |
| Glance | 2m03s | 1m45s |
| Placement | 1m15s | 1m12s |
| Compute | 11m17s | 6m18s |
| Network | 5m59s | 3m33s |
| Orchestration | 1m49s | 1m44s |
| Dashboard | 5m57s | 5m58s |

Manifest and lock finalization completed in 38s. The two parent summaries
built exactly 8 shared parents with no failures. The 14 leaf summaries built
exactly their planned service-group images with no failures and reported each
pre-pulled parent chain as skipped. All 18 workflow jobs reported zero
annotations.

## Published Images

| Image | Deploy ref | Manifest digest |
| --- | --- | --- |
| `keystone` | `ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9` | `sha256:d022e6c334c567219fdff29995507aeec932d8091cca3c2e000a452652405a0a` |
| `keystone-fernet` | `ghcr.io/supergate-jhbyun/kolla-image-build/keystone-fernet:2025.1-rocky-9` | `sha256:95fe12d70052f5dfc071ff04bce02a14eaf8b9a10cd57c1b44c7bafba66117b6` |
| `keystone-ssh` | `ghcr.io/supergate-jhbyun/kolla-image-build/keystone-ssh:2025.1-rocky-9` | `sha256:e66d820c310eabc9852a509331f6771600476afb792c47eaf238d1ab22ff75e4` |
| `glance-api` | `ghcr.io/supergate-jhbyun/kolla-image-build/glance-api:2025.1-rocky-9` | `sha256:b58d76622e9c73fc7f66f4ed7965cb73ad6c439b5c624f815513766834176c8f` |
| `placement-api` | `ghcr.io/supergate-jhbyun/kolla-image-build/placement-api:2025.1-rocky-9` | `sha256:14dd93494ac2c1eabbcfe331283d0a5614a51c3a66fbde9bd8c388da779b0d65` |
| `nova-api` | `ghcr.io/supergate-jhbyun/kolla-image-build/nova-api:2025.1-rocky-9` | `sha256:7bd1effa8168eee906904cacee4fb243c5a5ae571dafcf21ecf50501c488347d` |
| `nova-scheduler` | `ghcr.io/supergate-jhbyun/kolla-image-build/nova-scheduler:2025.1-rocky-9` | `sha256:6a71fb28794389930de25196b4c3ea00a9d187d31b29c2b06412f027c135b603` |
| `nova-conductor` | `ghcr.io/supergate-jhbyun/kolla-image-build/nova-conductor:2025.1-rocky-9` | `sha256:31a06e8976b76d3a0c89f180d8e5f9f1c322f45b0670004fb7c0441d5f9fb724` |
| `nova-compute` | `ghcr.io/supergate-jhbyun/kolla-image-build/nova-compute:2025.1-rocky-9` | `sha256:1c5d9c00e8a88d491a9272323e6870ddd7be491b4e4286d4a56f27aaee2ddbfc` |
| `nova-libvirt` | `ghcr.io/supergate-jhbyun/kolla-image-build/nova-libvirt:2025.1-rocky-9` | `sha256:0e3550f5ca51390b789b9dc25fcd1c2d8ae18b5627a6b6f0e83a419a2d373bf9` |
| `nova-ssh` | `ghcr.io/supergate-jhbyun/kolla-image-build/nova-ssh:2025.1-rocky-9` | `sha256:5ece4df60aa801fd81a2a0d0f0e3f61c9a1f1322b29c5c84cb6796016622688d` |
| `nova-novncproxy` | `ghcr.io/supergate-jhbyun/kolla-image-build/nova-novncproxy:2025.1-rocky-9` | `sha256:d27e71a8c0cf90b0a3aa042d81060c2f7f2ce84077839483edec638c4f470a54` |
| `neutron-server` | `ghcr.io/supergate-jhbyun/kolla-image-build/neutron-server:2025.1-rocky-9` | `sha256:b6bf4f9245681dbc3277c0ad0037e6ebc6d92626c11ef5737e68f4d8b42550d4` |
| `neutron-dhcp-agent` | `ghcr.io/supergate-jhbyun/kolla-image-build/neutron-dhcp-agent:2025.1-rocky-9` | `sha256:b037e27bf1391875bfdcc7d9adf8a1c1855871ff6a8099c2670e7dfb62289c77` |
| `neutron-l3-agent` | `ghcr.io/supergate-jhbyun/kolla-image-build/neutron-l3-agent:2025.1-rocky-9` | `sha256:9190933a399554a126f8292b7314f0ab530a39bd38f53839cdf8da734375127e` |
| `neutron-metadata-agent` | `ghcr.io/supergate-jhbyun/kolla-image-build/neutron-metadata-agent:2025.1-rocky-9` | `sha256:b3579d76d144ded4930e130c5de0ede6bb9f21fb826c7333b5b962849d28ed2b` |
| `neutron-openvswitch-agent` | `ghcr.io/supergate-jhbyun/kolla-image-build/neutron-openvswitch-agent:2025.1-rocky-9` | `sha256:25f60feb280a47e6ea91d33401de88d5fb2109d3d9cf82811578a45cdc2ac06c` |
| `heat-api` | `ghcr.io/supergate-jhbyun/kolla-image-build/heat-api:2025.1-rocky-9` | `sha256:88a4e778f94561f0770cbf3c73efa907dbb9698df1b8e28886ad76107b6ebaa3` |
| `heat-api-cfn` | `ghcr.io/supergate-jhbyun/kolla-image-build/heat-api-cfn:2025.1-rocky-9` | `sha256:491b7c0a6b9ad60d9119a6ddea846787d406a49b5607cb887a86358d10f831cb` |
| `heat-engine` | `ghcr.io/supergate-jhbyun/kolla-image-build/heat-engine:2025.1-rocky-9` | `sha256:d0fa717c65df14ae316c3266a4ea46b4ba7d3726897b1a6b72fe157d4dc83760` |
| `horizon` | `ghcr.io/supergate-jhbyun/kolla-image-build/horizon:2025.1-rocky-9` | `sha256:8b30759629167ff1670560207edcbfe7ecb9f11a0ed9789ac874e28aca5a6d44` |

The downloaded full publish summary passed
`scripts/validate-publish-summary.py`. Its 21 metadata files contain valid
`sha256` manifest digests and its 42 architecture records match the publish
plan.

## Staging Lock

Lock file: `locks/stg/core-2025.1-rocky-9.yml`

The lock is the exact generated workflow artifact. It contains all 22
Kolla-Ansible variables required by the core profile and pins every deploy ref
to the manifest digest above. It passed:

```text
python3 scripts/validate-lock.py \
  --environment stg \
  --profile core \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  locks/stg/core-2025.1-rocky-9.yml
```

## GHCR Verification

All 21 package pages reported `Public`. With an empty Docker configuration,
`docker buildx imagetools inspect` succeeded for all 21 deploy refs. Every
remote digest matched the publish summary and every manifest contained exactly
`linux/amd64` and `linux/arm64`.

Anonymous full pulls of the representative `nova-compute` deploy ref also
succeeded for both platforms. Local OCI verification recomputed every
manifest, config, and layer digest:

```text
linux/amd64 sha256:c20a50d1c683cf452c86056523cb8cf594f8f1f0cfcc135430c4a0e3375e0096
  48 layers, 715288079 verified bytes
linux/arm64 sha256:4bfb38e4afe4120fae339fdc4444ef73d0208aa28ad19b26de60f31459a12b82
  49 layers, 678162448 verified bytes
```

The one-time `ALLOW_GHCR_FULL_CORE_PUBLISH` repository variable was restored
to `false` after the workflow completed.
