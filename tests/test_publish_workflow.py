from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISH_WORKFLOW = ROOT / ".github" / "workflows" / "publish.yml"


class PublishWorkflowTest(unittest.TestCase):
    def test_image_all_is_available_for_full_profile_dry_runs(self) -> None:
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("description: Smoke publish image, or all for a full-profile dry run", workflow)
        self.assertIn("          - all", workflow)
        self.assertIn("if [ '${{ inputs.image }}' != 'all' ]; then", workflow)
        self.assertIn("plan_args+=(--image '${{ inputs.image }}')", workflow)

    def test_real_publish_guard_still_restricts_to_keystone(self) -> None:
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('[ "${{ inputs.image }}" != "keystone" ]', workflow)
        self.assertIn(
            "The first smoke publish is restricted to core/keystone 2025.1-rocky-9.",
            workflow,
        )

    def test_real_publish_validates_partial_and_full_summary_artifacts(self) -> None:
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("name: Validate publish summary", workflow)
        self.assertIn("scripts/validate-publish-summary.py", workflow)
        self.assertIn("--allow-partial", workflow)
        self.assertIn("if [ '${{ inputs.image }}' != 'all' ]; then", workflow)
        self.assertIn("name: Generate and validate full-profile lock", workflow)
        self.assertIn("scripts/generate-lock.py", workflow)
        self.assertIn("scripts/validate-lock.py", workflow)

    def test_real_publish_uses_parent_and_service_group_matrices(self) -> None:
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("name: Render parent and service build matrices", workflow)
        self.assertIn('return "ubuntu-24.04-arm" if arch == "arm64" else "ubuntu-24.04"', workflow)
        self.assertIn("parent_matrix: ${{ steps.build-matrix.outputs.parent_matrix }}", workflow)
        self.assertIn("build_matrix: ${{ steps.build-matrix.outputs.build_matrix }}", workflow)
        self.assertIn("name: Build shared parents ${{ matrix.arch }}", workflow)
        self.assertIn("matrix: ${{ fromJson(needs.publish-plan.outputs.parent_matrix) }}", workflow)
        self.assertIn("name: Build ${{ matrix.group }} ${{ matrix.arch }}", workflow)
        self.assertIn("runs-on: ${{ matrix.runner }}", workflow)
        self.assertIn("matrix: ${{ fromJson(needs.publish-plan.outputs.build_matrix) }}", workflow)
        self.assertIn("max-parallel: 8", workflow)
        self.assertIn('for parent_ref in arch["parent_refs"]:', workflow)
        self.assertIn('["docker", "pull", "--platform", arch["platform"], parent_ref]', workflow)
        self.assertNotIn("docker/setup-qemu-action", workflow)

    def test_real_publish_finalizes_manifest_after_architecture_builds(self) -> None:
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("finalize-publish:", workflow)
        self.assertIn("name: Finalize manifests and lock", workflow)
        self.assertIn("- build-images", workflow)
        self.assertIn("pattern: kolla-leaf-*-${{ inputs.release }}-${{ inputs.distro }}-${{ inputs.distro_version }}", workflow)
        self.assertIn("merge-multiple: true", workflow)
        self.assertIn('logs_dir / f"{image_name}-manifest-create.log"', workflow)
        self.assertIn('manifests_dir / f"{image_name}-publish-summary.json"', workflow)

    def test_publish_flow_serializes_tag_writers_and_bounds_jobs(self) -> None:
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("concurrency:", workflow)
        self.assertIn(
            "group: kolla-publish-${{ inputs.release }}-${{ inputs.distro }}-"
            "${{ inputs.distro_version }}-${{ inputs.profile }}",
            workflow,
        )
        self.assertIn("cancel-in-progress: false", workflow)
        self.assertIn("timeout-minutes: 90", workflow)
        self.assertIn("timeout-minutes: 20", workflow)
        self.assertNotIn("  packages: write\n\nenv:", workflow)

    def test_real_publish_accepts_buildx_descriptor_metadata_digest(self) -> None:
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('manifest_metadata.get("containerimage.digest")', workflow)
        self.assertIn('manifest_metadata.get("containerimage.descriptor")', workflow)
        self.assertIn('manifest_digest = descriptor.get("digest")', workflow)


if __name__ == "__main__":
    unittest.main()
