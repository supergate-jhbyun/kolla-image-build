#!/usr/bin/env python3
"""Create a dry-run publish plan for Kolla image artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "config" / "build-matrix.json"
PROFILES_DIR = ROOT / "config" / "profiles"
ARCH_TO_KOLLA_BASE_ARCH = {
    "amd64": "x86_64",
    "arm64": "aarch64",
}
ARCH_TO_PLATFORM = {
    "amd64": "linux/amd64",
    "arm64": "linux/arm64",
}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file_obj:
        return json.load(file_obj)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a dry-run Kolla image publish plan from repository config."
    )
    parser.add_argument("--profile", required=True, help="Profile name under config/profiles")
    parser.add_argument("--release", required=True, help="OpenStack release, for example 2025.1")
    parser.add_argument("--distro", required=True, help="Base distro name, for example rocky")
    parser.add_argument("--distro-version", required=True, help="Base distro version, for example 9")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Required safety flag. This planner never builds or pushes images.",
    )
    return parser.parse_args()


def find_distro(matrix: dict[str, Any], name: str, version: str) -> dict[str, str]:
    for distro in matrix["distros"]:
        if distro["name"] == name and distro["version"] == version:
            return distro
    raise ValueError(f"unsupported distro/version: {name}-{version}")


def load_profile(name: str) -> dict[str, Any]:
    profile_path = PROFILES_DIR / f"{name}.json"
    if not profile_path.exists():
        raise ValueError(f"profile does not exist: {profile_path.relative_to(ROOT)}")
    profile = load_json(profile_path)
    if profile.get("name") != name:
        raise ValueError(f"profile name mismatch in {profile_path.relative_to(ROOT)}")
    return profile


def render_tag(template: str, release: str, distro: dict[str, str], arch: str | None = None) -> str:
    values = {
        "release": release,
        "distro": distro["name"],
        "distro_version": distro["version"],
        "arch": arch or "",
    }
    return template.format(**values)


def image_ref(registry: str, owner: str, repository: str, image: str, tag: str) -> str:
    return f"{registry}/{owner}/{repository}/{image}:{tag}"


def manifest_metadata_file(image: str, deploy_tag: str) -> str:
    return f"artifacts/manifests/{image}-{deploy_tag}.json"


def kolla_build_command(
    registry: str,
    owner: str,
    repository: str,
    image: str,
    release: str,
    distro: dict[str, str],
    arch: str,
    arch_tag: str,
) -> list[str]:
    return [
        "kolla-build",
        "--engine",
        "docker",
        "--base",
        distro["name"],
        "--base-tag",
        distro["version"],
        "--base-arch",
        ARCH_TO_KOLLA_BASE_ARCH[arch],
        "--platform",
        ARCH_TO_PLATFORM[arch],
        "--openstack-release",
        release,
        "--registry",
        registry,
        "--namespace",
        f"{owner}/{repository}",
        "--tag",
        arch_tag,
        "--push",
        f"^{image}$",
    ]


def build_plan(
    matrix: dict[str, Any],
    profile: dict[str, Any],
    release: str,
    distro: dict[str, str],
) -> dict[str, Any]:
    tag_policy = matrix["tag_policy"]
    registry = matrix["registry"]
    owner = matrix["owner"]
    repository = matrix["repository"]
    deploy_tag = render_tag(tag_policy["deploy_tag_template"], release, distro)

    images = []
    for image in profile["images"]:
        architectures = []
        for arch in matrix["architectures"]:
            arch_tag = render_tag(tag_policy["arch_tag_template"], release, distro, arch)
            arch_ref = image_ref(registry, owner, repository, image, arch_tag)
            architectures.append(
                {
                    "arch": arch,
                    "arch_tag": arch_tag,
                    "arch_ref": arch_ref,
                    "expected_ghcr_ref": arch_ref,
                    "kolla_base_arch": ARCH_TO_KOLLA_BASE_ARCH[arch],
                    "platform": ARCH_TO_PLATFORM[arch],
                    "commands": {
                        "kolla_build_push": kolla_build_command(
                            registry,
                            owner,
                            repository,
                            image,
                            release,
                            distro,
                            arch,
                            arch_tag,
                        )
                    },
                }
            )

        deploy_ref = image_ref(registry, owner, repository, image, deploy_tag)
        arch_refs = [arch_plan["arch_ref"] for arch_plan in architectures]
        metadata_file = manifest_metadata_file(image, deploy_tag)
        images.append(
            {
                "image": image,
                "deploy_tag": deploy_tag,
                "deploy_ref": deploy_ref,
                "expected_ghcr_ref": deploy_ref,
                "manifest_metadata_file": metadata_file,
                "architectures": architectures,
                "commands": {
                    "manifest_create": [
                        "docker",
                        "buildx",
                        "imagetools",
                        "create",
                        "--tag",
                        deploy_ref,
                        "--metadata-file",
                        metadata_file,
                        *arch_refs,
                    ],
                    "manifest_inspect": [
                        "docker",
                        "buildx",
                        "imagetools",
                        "inspect",
                        deploy_ref,
                    ],
                },
            }
        )

    return {
        "dry_run": True,
        "release": release,
        "distro": distro["name"],
        "distro_version": distro["version"],
        "profile": profile["name"],
        "registry": registry,
        "owner": owner,
        "repository": repository,
        "images": images,
    }


def main() -> int:
    args = parse_args()
    if not args.dry_run:
        print("Refusing to render publish plan without --dry-run.", file=sys.stderr)
        return 2

    matrix = load_json(MATRIX_PATH)
    if args.release != matrix["release"]:
        print(f"Unsupported release: {args.release}", file=sys.stderr)
        return 2

    try:
        distro = find_distro(matrix, args.distro, args.distro_version)
        profile = load_profile(args.profile)
        plan = build_plan(matrix, profile, args.release, distro)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    print(json.dumps(plan, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
