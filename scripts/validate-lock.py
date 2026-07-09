#!/usr/bin/env python3
"""Validate Kolla-Ansible image lock files for environment promotion policy."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "config" / "build-matrix.json"
PROFILES_DIR = ROOT / "config" / "profiles"
DIGEST_RE = re.compile(r"^sha256:[a-f0-9]{64}$")
LOCK_LINE_RE = re.compile(r"^([A-Za-z0-9_]+):\s*['\"]?([^'\"]+)['\"]?\s*$")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as file_obj:
        return json.load(file_obj)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate generated Kolla-Ansible *_image_full lock files."
    )
    parser.add_argument("--environment", required=True, choices=["dev", "stg", "prod"])
    parser.add_argument("--profile", required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--distro", required=True)
    parser.add_argument("--distro-version", required=True)
    parser.add_argument("lock_file", type=Path)
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


def render_tag(template: str, release: str, distro: dict[str, str]) -> str:
    return template.format(
        release=release,
        distro=distro["name"],
        distro_version=distro["version"],
    )


def expected_variable_images(profile: dict[str, Any]) -> dict[str, str]:
    variables: dict[str, str] = {}
    for image_entry in profile["images"]:
        for variable in image_entry["kolla_ansible_variables"]:
            variables[variable] = image_entry["name"]
    return variables


def parse_lock(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        match = LOCK_LINE_RE.fullmatch(line)
        if not match:
            raise ValueError(f"{path}:{line_number} is not a simple key: value lock line")

        key, value = match.groups()
        if key in values:
            raise ValueError(f"{path}:{line_number} duplicates lock key: {key}")
        values[key] = value
    return values


def validate_ref(
    variable: str,
    value: str,
    expected_image: str,
    deploy_tag: str,
    registry: str,
    owner: str,
    repository: str,
    environment: str,
) -> list[str]:
    errors: list[str] = []
    expected_prefix = f"{registry}/{owner}/{repository}/{expected_image}:{deploy_tag}"

    if "@" in value:
        ref, digest = value.rsplit("@", 1)
        if ref != expected_prefix:
            errors.append(f"{variable} must use {expected_prefix}, got {ref}")
        if not DIGEST_RE.fullmatch(digest):
            errors.append(f"{variable} digest must be sha256:<64 hex chars>")
    else:
        if value != expected_prefix:
            errors.append(f"{variable} must use {expected_prefix}, got {value}")
        if environment in {"stg", "prod"}:
            errors.append(f"{environment} lock {variable} must be digest pinned")

    return errors


def validate_lock(
    matrix: dict[str, Any],
    profile: dict[str, Any],
    release: str,
    distro: dict[str, str],
    environment: str,
    values: dict[str, str],
) -> list[str]:
    deploy_tag = render_tag(matrix["tag_policy"]["deploy_tag_template"], release, distro)
    expected_variables = expected_variable_images(profile)
    errors: list[str] = []

    missing = sorted(set(expected_variables) - set(values))
    unknown = sorted(set(values) - set(expected_variables))
    for variable in missing:
        errors.append(f"missing lock variable: {variable}")
    for variable in unknown:
        errors.append(f"unknown lock variable: {variable}")

    for variable, expected_image in expected_variables.items():
        value = values.get(variable)
        if value is None:
            continue
        errors.extend(
            validate_ref(
                variable,
                value,
                expected_image,
                deploy_tag,
                matrix["registry"],
                matrix["owner"],
                matrix["repository"],
                environment,
            )
        )
    return errors


def main() -> int:
    args = parse_args()
    matrix = load_json(MATRIX_PATH)
    errors: list[str] = []

    try:
        if args.release != matrix["release"]:
            raise ValueError(f"unsupported release: {args.release}")
        distro = find_distro(matrix, args.distro, args.distro_version)
        profile = load_profile(args.profile)
        values = parse_lock(args.lock_file)
        errors = validate_lock(
            matrix,
            profile,
            args.release,
            distro,
            args.environment,
            values,
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if errors:
        print("Lock validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Lock validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
