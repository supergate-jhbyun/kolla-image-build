# Environment Lock Files

This directory is reserved for Kolla-Ansible image locks promoted by
environment.

Expected paths:

```text
locks/dev/core-2025.1-rocky-9.yml
locks/dev/core-2025.1-ubuntu-24.04.yml
locks/stg/core-2025.1-rocky-9.yml
locks/stg/core-2025.1-ubuntu-24.04.yml
locks/prod/core-2025.1-rocky-9.yml
locks/prod/core-2025.1-ubuntu-24.04.yml
```

Do not commit placeholder lock YAML with fake digests. Generate locks from a
real publish summary:

```bash
python3 scripts/generate-lock.py \
  --publish-summary artifacts/publish-summary-2025.1-rocky-9.json \
  --profile core \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  --output locks/stg/core-2025.1-rocky-9.yml
```

Dev may use tag-only refs for rapid iteration. Stg and prod must validate with
digest-pinned refs:

```bash
python3 scripts/validate-lock.py \
  --environment stg \
  --profile core \
  --release 2025.1 \
  --distro rocky \
  --distro-version 9 \
  locks/stg/core-2025.1-rocky-9.yml
```

Production promotion should copy the staging-verified full digest set. Rollback
should restore an earlier production lock file.
