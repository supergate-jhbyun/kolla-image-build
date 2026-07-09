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

    def test_real_publish_validates_smoke_summary_artifact(self) -> None:
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("name: Validate smoke publish summary", workflow)
        self.assertIn("scripts/validate-publish-summary.py", workflow)
        self.assertIn("--allow-partial", workflow)
        self.assertIn("--image '${{ inputs.image }}'", workflow)

    def test_real_publish_accepts_buildx_descriptor_metadata_digest(self) -> None:
        workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")

        self.assertIn('manifest_metadata.get("containerimage.digest")', workflow)
        self.assertIn('manifest_metadata.get("containerimage.descriptor")', workflow)
        self.assertIn('manifest_digest = descriptor.get("digest")', workflow)


if __name__ == "__main__":
    unittest.main()
