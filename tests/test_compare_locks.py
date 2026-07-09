from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPARE_LOCKS = ROOT / "scripts" / "compare-locks.py"
PROFILE_PATH = ROOT / "config" / "profiles" / "core.json"


def digest(index: int) -> str:
    return f"sha256:{index:064x}"


def core_profile() -> dict:
    return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))


def lock_text(distro: str = "rocky", distro_version: str = "9") -> str:
    tag = f"2025.1-{distro}-{distro_version}"
    lines = ["# synthetic lock"]
    for index, image in enumerate(core_profile()["images"], 1):
        ref = (
            "ghcr.io/supergate-jhbyun/kolla-image-build/"
            f"{image['name']}:{tag}@{digest(index)}"
        )
        for variable in image["kolla_ansible_variables"]:
            lines.append(f'{variable}: "{ref}"')
    return "\n".join(lines) + "\n"


def run_compare(
    source: Path,
    target: Path,
    distro: str = "rocky",
    distro_version: str = "9",
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            str(COMPARE_LOCKS),
            "--profile",
            "core",
            "--release",
            "2025.1",
            "--distro",
            distro,
            "--distro-version",
            distro_version,
            str(source),
            str(target),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )


class CompareLocksTest(unittest.TestCase):
    def test_identical_locks_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source.yml"
            target = temp_path / "target.yml"
            source.write_text(lock_text(), encoding="utf-8")
            target.write_text(lock_text(), encoding="utf-8")

            result = run_compare(source, target)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Lock comparison passed.", result.stdout)

    def test_digest_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source.yml"
            target = temp_path / "target.yml"
            source.write_text(lock_text(), encoding="utf-8")
            target.write_text(lock_text().replace(digest(1), digest(999)), encoding="utf-8")

            result = run_compare(source, target)

            self.assertEqual(result.returncode, 1)
            self.assertIn("keystone_image_full differs", result.stderr)

    def test_missing_variable_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source.yml"
            target = temp_path / "target.yml"
            source.write_text(lock_text(), encoding="utf-8")
            target_lines = [
                line
                for line in lock_text().splitlines()
                if not line.startswith("keystone_image_full:")
            ]
            target.write_text("\n".join(target_lines) + "\n", encoding="utf-8")

            result = run_compare(source, target)

            self.assertEqual(result.returncode, 1)
            self.assertIn("target missing lock variable: keystone_image_full", result.stderr)

    def test_wrong_distro_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source = temp_path / "source.yml"
            target = temp_path / "target.yml"
            source.write_text(lock_text(), encoding="utf-8")
            target.write_text(lock_text(), encoding="utf-8")

            result = run_compare(source, target, "ubuntu", "24.04")

            self.assertEqual(result.returncode, 1)
            self.assertIn("2025.1-ubuntu-24.04", result.stderr)


if __name__ == "__main__":
    unittest.main()
