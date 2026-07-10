# Deployment 2025.1 Rocky 9 Publish Results

Date: 2026-07-10

## Scope

- Profile: `deployment`
- Selection: `all`
- Leaf images: 52
- Kolla-Ansible variables: 54
- Shared parents: 13
- Service groups: 17
- Platforms: `linux/amd64`, `linux/arm64`
- Commit: `90dd7ab65b41409dd055e1e7372da9dcbecb712b`
- Retries: none

This result creates only the deployment dev lock. It does not authorize a
web01 change, staging promotion, production promotion, Zot removal, or
destruction of the existing deployment.

## Dry Run

Workflow run:
<https://github.com/supergate-jhbyun/kolla-image-build/actions/runs/29067645616>

Result: success

The downloaded plan contained 52 leaf images, 54 Kolla-Ansible variables, 13
shared parents, 17 service groups, 2 native parent jobs, 34 native leaf jobs,
104 architecture refs, and 52 deploy refs. The expected role aliases map
`nova_super_conductor_image_full` to `nova-conductor` and
`neutron_ovn_metadata_agent_image_full` to `neutron-metadata-agent`.

## GHCR Publish

Workflow run:
<https://github.com/supergate-jhbyun/kolla-image-build/actions/runs/29067891260>

Result: success in 27m18s

The workflow used `ubuntu-24.04` for amd64 and `ubuntu-24.04-arm` for arm64.
It did not use QEMU. Shared parents completed in 10m18s for amd64 and 8m20s
for arm64. The 34 leaf jobs ran with a maximum parallelism of 8; final manifest
and lock generation completed in 1m19s.

All 38 jobs succeeded. The two parent summaries built exactly 13 parents per
architecture. The 34 leaf summaries built exactly 52 images per architecture,
reported the pre-pulled parent chains as skipped, and contained no failures.
All 38 check runs reported zero annotations.

## Artifact Validation

All 38 workflow artifacts were downloaded. The 423 JSON files parsed
successfully. Cross-artifact checks verified:

- 26 parent build records
- 104 leaf build records
- 104 architecture metadata records
- 52 deploy manifest metadata records
- 52 per-image publish records
- 70 Kolla build summaries with `failed=[]`
- 38 identical publish-plan copies

The final summary passed `scripts/validate-publish-summary.py`. Regenerating
the lock produced a byte-identical file with SHA-256
`4bacf13c005555f11eb5aed8028dc5a24fa8c3a672078ec96734f7fef6628b1d`.

## Published Images

| Image | Manifest digest |
| --- | --- |
| `cron` | `sha256:fe357175b25475aec0046dcfb08481f5b8f4466d91ed98bde027d07600db8c19` |
| `fluentd` | `sha256:b5992e74c24897838a075ab720df12a047bdffa39dfd142c0639a66f3ca13480` |
| `glance-api` | `sha256:5d0e1dfc6411795b3b28fdbd01b0ae61c7677cc39221870b333a7b38e83418fe` |
| `grafana` | `sha256:b6c84eac720fe3ba1c6ec066b2c8c42f2dfd427ac050cf96646fa135770353cb` |
| `haproxy` | `sha256:28a714538f7fc7879eb8dc3e595df7e50a7f0f6d997d63342f99e1b86f86affa` |
| `heat-api` | `sha256:5f7e5cdca4a8ea0dc31b2afe90b357bc997af1ebdcb9a5b859917adbb830063c` |
| `heat-api-cfn` | `sha256:f9dfe74094d58ab19c3d56b0e27ee1e514a4c4553cf03780e2285b12ba94df8a` |
| `heat-engine` | `sha256:fef26fcb41af99a17cd0972d2b0d4bc4a9578fd31948602ed4c31b0068dd7572` |
| `horizon` | `sha256:4530c2e5aff621fed4aaca9a62f0070d730ccca89c65b0b41cb1d0493c865233` |
| `keepalived` | `sha256:9c223d488b5217de659f8f41619f60b1743bfe30684c3fec805db16a07b6db7a` |
| `keystone` | `sha256:4381e5877a1a1fbc9ddb6cd6d66f41bcfb0556a2b66daed9203cdcadcac46db4` |
| `keystone-fernet` | `sha256:edcb6c49d5a04aa1c54942744378c9dea042cda60c72efd46b517c403a688a2c` |
| `keystone-ssh` | `sha256:2d457be587eb19d502148750cb698750b1d3b4db58b9b221ba46b2c26ac59526` |
| `kolla-toolbox` | `sha256:1ae240a823d5dc472ceadf5c0b3407a604235d2303fb1dfa1f1b85c0f28e5bbc` |
| `mariadb-server` | `sha256:711e15ada30304d858b318f5470a65fb4250227c14d7877a1d4d3b4d7b55b330` |
| `memcached` | `sha256:decbea579d63cf777e24f19e7d90dff23d62f39eedcd95ab51387235e52f87d2` |
| `neutron-metadata-agent` | `sha256:1e06fc40d0a26593d9594286364119a622fcbce4affe032c2b57d8742a6074ff` |
| `neutron-server` | `sha256:ec75d72c8b670e4e928a43908866dcca7812d3345f5664da3f6bb9bc5c0c417d` |
| `nova-api` | `sha256:50a75f4315a03c962163f50a1ae88f101a98eadb59c25ba663a3eff45c1416e9` |
| `nova-compute` | `sha256:cc3fd33bdc52e4f3b5c6da6cf5ca7596b2af8b3aa7c8d96097fc35ab96635689` |
| `nova-conductor` | `sha256:21091047f517e0bd9e405e70ce68f001d28aae6b66b09fd7f575e2a430c6f272` |
| `nova-libvirt` | `sha256:4b111facac6d6296bac95076e70437dbb8e3c8a3c4f88a729464e3c9c0dc118d` |
| `nova-novncproxy` | `sha256:d1aa61769e1414af5f68897c4fcb46a10b4603e73174fac90c2c396d3322ca57` |
| `nova-scheduler` | `sha256:c6bc2f1ff3b640723e7a096c6edd6188338e725591986a3c068d940b515935f7` |
| `nova-ssh` | `sha256:0686ba3fe0f1179c0e0c700aeeb0187396048e11b5890e9d76c1f2b7bfeffff1` |
| `octavia-api` | `sha256:3628a08cb7d260eda11d2a4b2443c9086b6d42d0dbb6f91fdc2d3a1af9ed34a7` |
| `octavia-driver-agent` | `sha256:9b72002f4b8293c8de97abfd295ff4f67d6b94d552a688ec161c49c87c6269c8` |
| `octavia-health-manager` | `sha256:08d7be4c65aef4186d7d17cae11ac0bbca412989beeb5ed801c31d65d05729b8` |
| `octavia-housekeeping` | `sha256:12d1f8062bb29fcd6412f6ea11aa8f88c8393dd6615e670f89c6f8aa67d1c2a0` |
| `octavia-worker` | `sha256:42c5f103594541d94626ef52bab9032d1a4dadf82b9a4202d251b04039dd8349` |
| `opensearch` | `sha256:2373f80ca12882a305f444a99249afd21bb19bbf7c5342d30d88a56c453ff540` |
| `opensearch-dashboards` | `sha256:55b75d7435f84741877625f1b9ed27b2e41328e34e6a07e7990b0047b01ac46a` |
| `openvswitch-db-server` | `sha256:c7df4dfff10af9ac0f859bfe8e0ec640c418e206e22ce20e136fe686a3449c5a` |
| `openvswitch-vswitchd` | `sha256:eedea0965a7b4e3b844f3933fa1cc4fd17d3d1c4c7c307a8991d81c60197e502` |
| `ovn-controller` | `sha256:4359d4803e17b7f6a93de434dbede62467257f51d982354c0303009689a10f39` |
| `ovn-nb-db-server` | `sha256:cc0df1bc18311ece0e09055eae0bf925a75506b6591796513b15e2e5d4658bbb` |
| `ovn-northd` | `sha256:d350cefc51e428ad1b99c715e0ecf036e559a7d15f7c4a24c9e0c63a789fde48` |
| `ovn-sb-db-relay` | `sha256:14a0dc7b31c63b63abe75c103b18c3c829b59562547544093bf3a9dbee57cb8e` |
| `ovn-sb-db-server` | `sha256:6cc60eb893c02362cb831fe7836a3e7de7c9abe115854f0b25e8934fb5847298` |
| `placement-api` | `sha256:f9dd5bd10fa7b9d93121d4f0b4f23a1c4237c9cfb0cd9af17bd0cf242c1e2fb0` |
| `prometheus-alertmanager` | `sha256:9ac1d4a520747eb53796bbcf56a353d8f83ae5efb9891a23ca834d293a57f1ad` |
| `prometheus-blackbox-exporter` | `sha256:06632fa84e27893e3aec199f4d15d743c685d4f69ef291ac7fa41f77172b26e0` |
| `prometheus-cadvisor` | `sha256:243f62813893ce27504827b83251a92da8cbd83e82dfa1ef306c3acd0d2afd25` |
| `prometheus-elasticsearch-exporter` | `sha256:b049a509c78fa7cdc12ba0773dcd118567f93af33249a673cdf707a87b0c569c` |
| `prometheus-libvirt-exporter` | `sha256:c1fd9c342d851e51e7be48d84ffd551bafd20ab0002b830b15cc4762477b8c7b` |
| `prometheus-memcached-exporter` | `sha256:d82ed8c0874ac0de6846f4dc4bccd08379c34a895804cb1b5af545450b4e45a5` |
| `prometheus-mysqld-exporter` | `sha256:2035214fbe6a81e0407baccf5087474c9dafed78b1574142a40613905acd311a` |
| `prometheus-node-exporter` | `sha256:cd2ec2f5535c0434d08b522914df58c24dd1e78392cdb930e1241165868e5dc4` |
| `prometheus-openstack-exporter` | `sha256:382532c8e8475a684b31c15fa793070722f8eed9d3e7c8e5195a8ab850391d39` |
| `prometheus-server` | `sha256:1648462c1d318f09c48abee4b387b68c4c55d0c4ca1a75c983df4260dab40c26` |
| `proxysql` | `sha256:60078e179619a64050348427824b6ea89b19e0d395cd7ad49d261cc4a942869d` |
| `rabbitmq` | `sha256:57ad762e7288bd68caaa8788ea3e30bcd62744aa85e4c08d43ef76564c406b6d` |

## Dev Lock

Lock file: `locks/dev/deployment-2025.1-rocky-9.yml`

The lock is byte-identical to the workflow artifact, contains all 54 expected
variables, and pins every deploy ref to a manifest digest. It passed:

```text
python3 scripts/validate-lock.py \
  --environment dev \
  --profile deployment \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  locks/dev/deployment-2025.1-rocky-9.yml
```

No staging or production deployment lock was created.

## GHCR Verification

All 52 package pages were reachable without a GitHub session and exposed the
exact package title. With a Docker configuration containing no files or GHCR
credentials, `docker buildx imagetools inspect` succeeded for every deploy,
amd64, and arm64 ref: 156 anonymous registry requests in total.

Every deploy digest matched the publish summary. Every deploy manifest
contained exactly `linux/amd64` and `linux/arm64`, and every child digest
matched its architecture-specific tag.

Anonymous full pulls of the representative `nova-compute` deploy ref succeeded
for both platforms:

```text
deploy  sha256:cc3fd33bdc52e4f3b5c6da6cf5ca7596b2af8b3aa7c8d96097fc35ab96635689
amd64   sha256:91934d1657bdf06a800b881d8c7bb1a953bb8e59aa6463a70107f38efe575f99
arm64   sha256:b3a617f30898dcbe588132d718941c176f9323d3d017a14be2ff20a08ad549ce
```

Local image inspection after each pull reported the requested architecture.
The temporary `ALLOW_GHCR_DEPLOYMENT_PUBLISH` repository variable was restored
to `false` immediately after the workflow completed.

## web01 Gate B Preflight And Canary

Gate B ran on 2026-07-10 after the exact approval phrase was received. The
deployment state was revalidated before changes: control02, compute02,
monitoring01, and horizon-022 were all `aarch64`; all 69 containers were
running with no unhealthy or exited containers; and server, image, network,
subnet, router, floating IP, load balancer, and stack counts were all zero.

The protected rollback baseline is stored on web01 at:

```text
/data/kolla-ansible-deploy/backups/ghcr-canary-20260710T051114Z
```

The directory mode is `0700`, and archives that contain deployment
configuration or credentials are `0600`. The baseline archives passed a full
listing check and have these SHA-256 values:

```text
4141845b8afc4c7dd5b1371b875a5520b5678b5126e673ca037ff739b5a23c42  kolla-config.tar.zst
a2928042087f3a91dc000ea823c394b55d4c581b88a801ae6530ab3556a97b74  zot-config-storage.tar.zst
bc2dbcb2ab8eeb32429ed17101d0c4785fb62ce31c9667f23a818fa96198f724  evidence.tar.zst
```

An XFS reflink snapshot of Zot storage was also created. An external 6.3 GiB
copy under `.context/web01-backups/ghcr-canary-20260710T051114Z` passed the
same checksum file. `passwords.yml` remained byte-identical throughout Gate B,
and `kolla-genpwd` was not run.

The verified dev lock was installed at
`/data/kolla-ansible-deploy/etc/kolla/globals.d/90-deployment-image-lock.yml`.
Its SHA-256 is
`4bacf13c005555f11eb5aed8028dc5a24fa8c3a672078ec96734f7fef6628b1d`,
and its 54 variables resolve to 52 unique digest-pinned leaf images. The four
global image defaults are now:

```yaml
docker_registry: "ghcr.io"
docker_namespace: "supergate-jhbyun/kolla-image-build"
docker_registry_insecure: "no"
openstack_tag_suffix: ""
```

`kolla-ansible prechecks` completed with no failed or unreachable hosts. Its
log loaded the `globals.d` lock and contained zero `web01:5000` references.

### Kolla-Ansible Digest Compatibility

The first `kolla-ansible pull` exposed a Kolla-Ansible 20.4.1.dev10 Docker
worker incompatibility. It split `repository:tag@sha256:digest` at the final
colon and sent the digest hex to Docker as a tag, producing a 404. A direct
`docker pull` of the same full reference succeeded on control02 and resolved
the expected `linux/arm64` image.

The compatibility fix was developed test-first. Four digest tests failed
against the original worker, then passed after the fix. The complete Docker
worker test module passed 123 of 123 tests, followed by `flake8` and
`git diff --check`. The actual four-node pull then completed with no failed or
unreachable hosts. Independent Docker metadata inspection found exactly all
52 locked digests and no extras; every image reported `linux/arm64`.

The web01 Kolla-Ansible checkout remains based on
`d72865ea088215e06faba85bb79e67d031e46818` and carries local commit
`75a9c05c209a1b57474428fd85e2717fa81e336e`. The reproducible patch is
`patches/kolla-ansible/0001-kolla_container-support-digest-pinned-Docker-images.patch`
with SHA-256
`baeb3871392b8957cbeae4ec0f492a5f4ca5b5b9c9b9970b1030f1757d7e6bab`.

### Canary Result

The first limited Horizon attempt stopped before changing a container because
delegated fact gathering reused the Rocky 9 Python 3.9 path on the Rocky 10
control host. The canary commands were retried with
`-e ansible_python_interpreter=auto_silent`, allowing per-host discovery.

Horizon on horizon-022 was reconfigured first, followed by Keystone,
Keystone fernet, and Keystone SSH on control02. All four running containers
use their exact lock references and `linux/arm64` images:

```text
horizon            sha256:4530c2e5aff621fed4aaca9a62f0070d730ccca89c65b0b41cb1d0493c865233
keystone           sha256:4381e5877a1a1fbc9ddb6cd6d66f41bcfb0556a2b66daed9203cdcadcac46db4
keystone-fernet    sha256:edcb6c49d5a04aa1c54942744378c9dea042cda60c72efd46b517c403a688a2c
keystone-ssh       sha256:2d457be587eb19d502148750cb698750b1d3b4db58b9b221ba46b2c26ac59526
```

Post-canary verification reported 69 running containers, zero unhealthy or
non-running containers, exactly four GHCR canary containers, and 65 unchanged
legacy Zot containers. Horizon returned HTTP 302 through both VIPs. Keystone
token creation returned HTTP 201 with a subject token, and authenticated
discovery returned HTTP 200. All user resource counts remained zero. The
successful pull and canary logs contain zero `web01:5000` references.

The compatibility patch is recorded in repository commit `0e6ab60`, and the
Gate B result is recorded in commit `0c67aba`. Push validation run
<https://github.com/supergate-jhbyun/kolla-image-build/actions/runs/29073281768>
completed successfully with one of one jobs passing and zero annotations.

Zot remains running. Stopping it, destroying the deployment, and deploying the
remaining 65 containers are outside Gate B and require their separate gates.
