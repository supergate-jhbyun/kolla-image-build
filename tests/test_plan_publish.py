from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN_PUBLISH = ROOT / "scripts" / "plan-publish.py"


def run_plan() -> dict:
    result = subprocess.run(
        [
            sys.executable,
            str(PLAN_PUBLISH),
            "--profile",
            "core",
            "--release",
            "2025.1",
            "--distro",
            "rocky",
            "--distro-version",
            "9",
            "--dry-run",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(result.stdout)


class PlanPublishTest(unittest.TestCase):
    def test_core_profile_images_are_included(self) -> None:
        plan = run_plan()
        image_names = {image["image"] for image in plan["images"]}

        self.assertEqual(
            image_names,
            {
                "keystone",
                "glance",
                "placement",
                "nova",
                "neutron",
                "heat",
                "horizon",
            },
        )

    def test_deploy_tags_do_not_include_arch(self) -> None:
        plan = run_plan()

        for image in plan["images"]:
            self.assertEqual(image["deploy_tag"], "2025.1-rocky-9")
            self.assertTrue(image["deploy_ref"].endswith(":2025.1-rocky-9"))
            self.assertFalse(image["deploy_tag"].endswith("-amd64"))
            self.assertFalse(image["deploy_tag"].endswith("-arm64"))

    def test_arch_tags_include_arch(self) -> None:
        plan = run_plan()

        for image in plan["images"]:
            arch_tags = {arch["arch"]: arch["arch_tag"] for arch in image["architectures"]}
            self.assertEqual(arch_tags["amd64"], "2025.1-rocky-9-amd64")
            self.assertEqual(arch_tags["arm64"], "2025.1-rocky-9-arm64")

    def test_expected_ghcr_refs_are_rendered(self) -> None:
        plan = run_plan()
        first_image = plan["images"][0]

        self.assertEqual(plan["registry"], "ghcr.io")
        self.assertEqual(plan["owner"], "supergate-jhbyun")
        self.assertEqual(
            first_image["expected_ghcr_ref"],
            "ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9",
        )
        self.assertEqual(
            first_image["architectures"][0]["expected_ghcr_ref"],
            "ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-amd64",
        )

    def test_kolla_build_commands_are_executable_arrays(self) -> None:
        plan = run_plan()
        first_arch = plan["images"][0]["architectures"][0]
        command = first_arch["commands"]["kolla_build_push"]

        self.assertEqual(command[0], "kolla-build")
        self.assertIn("--base", command)
        self.assertIn("rocky", command)
        self.assertIn("--base-tag", command)
        self.assertIn("9", command)
        self.assertIn("--base-arch", command)
        self.assertIn("x86_64", command)
        self.assertIn("--platform", command)
        self.assertIn("linux/amd64", command)
        self.assertIn("--registry", command)
        self.assertIn("ghcr.io", command)
        self.assertIn("--namespace", command)
        self.assertIn("supergate-jhbyun/kolla-image-build", command)
        self.assertIn("--tag", command)
        self.assertIn("2025.1-rocky-9-amd64", command)
        self.assertIn("--push", command)
        self.assertEqual(command[-1], "^keystone$")

    def test_manifest_commands_use_per_arch_refs(self) -> None:
        plan = run_plan()
        first_image = plan["images"][0]

        self.assertEqual(
            first_image["commands"]["manifest_create"],
            [
                "docker",
                "buildx",
                "imagetools",
                "create",
                "--tag",
                "ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9",
                "--metadata-file",
                "artifacts/manifests/keystone-2025.1-rocky-9.json",
                "ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-amd64",
                "ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9-arm64",
            ],
        )
        self.assertEqual(
            first_image["manifest_metadata_file"],
            "artifacts/manifests/keystone-2025.1-rocky-9.json",
        )
        self.assertEqual(
            first_image["commands"]["manifest_inspect"],
            [
                "docker",
                "buildx",
                "imagetools",
                "inspect",
                "ghcr.io/supergate-jhbyun/kolla-image-build/keystone:2025.1-rocky-9",
            ],
        )

    def test_refuses_without_dry_run(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(PLAN_PUBLISH),
                "--profile",
                "core",
                "--release",
                "2025.1",
                "--distro",
                "rocky",
                "--distro-version",
                "9",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--dry-run", result.stderr)


if __name__ == "__main__":
    unittest.main()
