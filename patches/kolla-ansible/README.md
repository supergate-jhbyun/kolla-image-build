# Kolla-Ansible digest image compatibility

Kolla-Ansible `stable/2025.1` at commit
`d72865ea088215e06faba85bb79e67d031e46818` splits a
`repository:tag@sha256:digest` reference at the digest colon. The Docker API
then attempts to pull the digest hex as a tag. It also checks only `RepoTags`,
which does not find a locally pulled tagged digest.

Apply the patch only after confirming the expected Kolla-Ansible base commit:

```bash
test "$(git rev-parse HEAD)" = d72865ea088215e06faba85bb79e67d031e46818
git am /path/to/0001-kolla_container-support-digest-pinned-Docker-images.patch
```

The patch keeps the existing tag-only path unchanged. For references that
contain `@`, it uses `inspect_image(full_ref)` and calls Docker SDK
`pull(repository=full_ref, tag=None)`.

Focused verification in the Kolla-Ansible checkout:

```bash
stestr run --serial \
  'TestImage.test_(check_image_digest|check_image_digest_not_found|get_image_id_digest|pull_image_digest)'
stestr run --serial tests.kolla_container_tests.test_docker_worker
```

The deployment still requires an actual `kolla-ansible pull` and target image
digest/platform validation. Unit tests alone do not prove registry or Docker
daemon compatibility.
