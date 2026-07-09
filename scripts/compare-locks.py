#!/usr/bin/env python3
"""Compare two Kolla-Ansible image locks for promotion parity."""

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
        description="Compare source and target Kolla-Ansible image locks."
    )
    parser.add_argument("--profile", required=True)
    parser.add_argument("--release", required=True)
    parser.add_argument("--distro", required=True)
    parser.add_argument("--distro-version", required=True)
    parser.add_argument("source_lock", type=Path)
    parser.add_argument("target_lock", type=Path)
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


def validate_lock_values(
    label: str,
    values: dict[str, str],
    expected_variables: dict[str, str],
    deploy_tag: str,
    matrix: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    missing = sorted(set(expected_variables) - set(values))
    unknown = sorted(set(values) - set(expected_variables))
    for variable in missing:
        errors.append(f"{label} missing lock variable: {variable}")
    for variable in unknown:
        errors.append(f"{label} unknown lock variable: {variable}")

    for variable, image in expected_variables.items():
        value = values.get(variable)
        if value is None:
            continue
        expected_prefix = (
            f"{matrix['registry']}/{matrix['owner']}/{matrix['repository']}/"
            f"{image}:{deploy_tag}"
        )
        if "@" not in value:
            errors.append(f"{label} {variable} must be digest pinned")
            continue
        ref, digest = value.rsplit("@", 1)
        if ref != expected_prefix:
            errors.append(f"{label} {variable} must use {expected_prefix}, got {ref}")
        if not DIGEST_RE.fullmatch(digest):
            errors.append(f"{label} {variable} digest must be sha256:<64 hex chars>")
    return errors


def compare_locks(source: dict[str, str], target: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for variable in sorted(set(source) | set(target)):
        source_value = source.get(variable)
        target_value = target.get(variable)
        if source_value != target_value:
            errors.append(
                f"{variable} differs: source={source_value!r}, target={target_value!r}"
            )
    return errors


def main() -> int:
    args = parse_args()
    errors: list[str] = []

    try:
        matrix = load_json(MATRIX_PATH)
        if args.release != matrix["release"]:
            raise ValueError(f"unsupported release: {args.release}")
        distro = find_distro(matrix, args.distro, args.distro_version)
        profile = load_profile(args.profile)
        deploy_tag = render_tag(matrix["tag_policy"]["deploy_tag_template"], args.release, distro)
        expected_variables = expected_variable_images(profile)
        source = parse_lock(args.source_lock)
        target = parse_lock(args.target_lock)
        errors.extend(
            validate_lock_values("source", source, expected_variables, deploy_tag, matrix)
        )
        errors.extend(
            validate_lock_values("target", target, expected_variables, deploy_tag, matrix)
        )
        if not errors:
            errors.extend(compare_locks(source, target))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if errors:
        print("Lock comparison failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print("Lock comparison passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
