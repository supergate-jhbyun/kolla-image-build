from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATE_APPROVAL = ROOT / "scripts" / "validate-publish-approval.py"
SMOKE_APPROVAL = (
    "I approve GHCR smoke publish for keystone 2025.1-rocky-9 from "
    "supergate-jhbyun/kolla-image-build."
)
FULL_CORE_APPROVAL = (
    "I approve GHCR full-core publish for core 2025.1-rocky-9 "
    "(21 images, amd64/arm64) from supergate-jhbyun/kolla-image-build."
)


def run_validator(
    *,
    image: str,
    approval: str,
    allow_smoke: str = "false",
    allow_full_core: str = "false",
    distro: str = "rocky",
    distro_version: str = "9",
) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env.update(
        {
            "ALLOW_GHCR_PUBLISH": allow_smoke,
            "ALLOW_GHCR_FULL_CORE_PUBLISH": allow_full_core,
            "APPROVAL": approval,
        }
    )
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATE_APPROVAL),
            "--profile",
            "core",
            "--image",
            image,
            "--release",
            "2025.1",
            "--distro",
            distro,
            "--distro-version",
            distro_version,
        ],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )


class PublishApprovalTest(unittest.TestCase):
    def test_keystone_smoke_scope_still_passes(self) -> None:
        result = run_validator(
            image="keystone",
            approval=SMOKE_APPROVAL,
            allow_smoke="true",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Smoke publish approval validated.", result.stdout)

    def test_approved_full_core_scope_passes(self) -> None:
        result = run_validator(
            image="all",
            approval=FULL_CORE_APPROVAL,
            allow_full_core="true",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Full-core publish approval validated.", result.stdout)

    def test_full_core_requires_dedicated_variable(self) -> None:
        result = run_validator(image="all", approval=FULL_CORE_APPROVAL)

        self.assertEqual(result.returncode, 1)
        self.assertIn("ALLOW_GHCR_FULL_CORE_PUBLISH=true", result.stderr)

    def test_full_core_rejects_wrong_approval_phrase(self) -> None:
        result = run_validator(
            image="all",
            approval=SMOKE_APPROVAL,
            allow_full_core="true",
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("exact full-core publish approval phrase", result.stderr)

    def test_smoke_variable_does_not_authorize_full_core(self) -> None:
        result = run_validator(
            image="all",
            approval=FULL_CORE_APPROVAL,
            allow_smoke="true",
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("ALLOW_GHCR_FULL_CORE_PUBLISH=true", result.stderr)

    def test_scope_change_is_rejected(self) -> None:
        result = run_validator(
            image="all",
            approval=FULL_CORE_APPROVAL,
            allow_full_core="true",
            distro="ubuntu",
            distro_version="24.04",
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("not approved for real publish", result.stderr)


if __name__ == "__main__":
    unittest.main()
