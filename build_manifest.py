#!/usr/bin/env python3
"""Build manifest.json and Documentation/manifest.sha256 automatically.

The script scans a package directory, calculates SHA-256 and size_bytes,
preserves package metadata from an existing manifest when available, validates
the rebuilt manifest against JSON Schema Draft 2020-12, and writes the files
atomically.

Examples:
  python build_manifest.py BeforeWeCloseTheGate_EP01_FINAL_PACKAGE
  python build_manifest.py PACKAGE --validate
  python build_manifest.py PACKAGE --dry-run --json

Exit codes:
  0  success
  10 package directory missing
  11 schema missing
  12 invalid JSON metadata/schema
  13 schema validation failure
  20 no payload files found
  50 runtime/internal error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import mimetypes
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

EXIT = {
    "PASS": 0,
    "PACKAGE_MISSING": 10,
    "SCHEMA_MISSING": 11,
    "JSON_ERROR": 12,
    "SCHEMA_FAIL": 13,
    "NO_FILES": 20,
    "INTERNAL": 50,
}

EXCLUDED_NAMES = {
    "manifest.json",
    "manifest.sha256",
    ".DS_Store",
    "Thumbs.db",
}
EXCLUDED_SUFFIXES = {
    ".artifactvalidatepass",
    ".artifactvalidatefixed",
    ".tmp",
    ".bak",
    ".orig",
}
CATEGORY_MAP = {
    "Canon": "canon",
    "Executive": "executive",
    "Editing": "editing",
    "Documentation": "documentation",
    "Tools": "documentation",
    ".github": "documentation",
}
MEDIA_TYPES = {
    ".zip": "application/zip",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".csv": "text/csv",
    ".md": "text/markdown",
    ".json": "application/json",
    ".py": "text/x-python",
    ".yml": "application/yaml",
    ".yaml": "application/yaml",
    ".txt": "text/plain",
}

DEFAULT_METADATA = {
    "manifest_version": "1.0",
    "package_id": "BWCTG-EP01-FINAL-20260929",
    "package_name": "BeforeWeCloseTheGate_EP01_FINAL_PACKAGE",
    "version": "FINAL",
    "release_date": "2026-09-29T18:30:00+07:00",
    "project": "Before We Close the Gate",
    "episode": "EP01",
    "episode_title": "นักสืบกับความกล้าที่อยู่ปลายเชือก",
    "status": {
        "canon_status": "MASTER_CANON",
        "cci": 96,
        "risk_level": "LOW",
        "production_status": "UNLOCKED",
        "release_status": "READY_FOR_EXECUTIVE_SIGN_OFF",
    },
    "metrics": {
        "scene_count": 11,
        "frame_count": 39,
        "image_prompts": 39,
        "motion_prompts": 39,
        "negative_prompts": 39,
    },
    "sla_policy": {
        "at_risk_threshold_percent": 20,
        "statuses": [
            "Completed",
            "On Track",
            "Pending",
            "At Risk",
            "Overdue",
            "Escalated",
        ],
    },
    "workflow_state": {
        "writing": "complete",
        "art": "complete",
        "animation": "complete",
        "editing": "complete",
        "qa": "complete",
        "executive_review": "pending",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False
    ) as handle:
        handle.write(text)
        temp_name = handle.name
    os.replace(temp_name, path)


def should_include(path: Path) -> bool:
    if path.name in EXCLUDED_NAMES:
        return False
    if any(path.name.endswith(suffix) for suffix in EXCLUDED_SUFFIXES):
        return False
    return not any(part in {"__pycache__", ".git"} for part in path.parts)


def media_type(path: Path) -> str:
    return MEDIA_TYPES.get(
        path.suffix.lower(),
        mimetypes.guess_type(path.name)[0] or "application/octet-stream",
    )


def category(relative_path: Path) -> str:
    return CATEGORY_MAP.get(relative_path.parts[0], "documentation")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_manifest(root: Path, metadata_path: Path | None) -> tuple[dict, list[str]]:
    existing_manifest = root / "manifest.json"
    metadata = dict(DEFAULT_METADATA)

    if existing_manifest.is_file():
        current = load_json(existing_manifest)
        for key in DEFAULT_METADATA:
            if key in current:
                metadata[key] = current[key]

    if metadata_path:
        overrides = load_json(metadata_path)
        for key, value in overrides.items():
            if key not in {"files", "file_count", "checksum_algorithm"}:
                metadata[key] = value

    payload_files = sorted(
        path for path in root.rglob("*") if path.is_file() and should_include(path)
    )
    if not payload_files:
        raise RuntimeError("No payload files found")

    entries = []
    for path in payload_files:
        rel = path.relative_to(root)
        entries.append(
            {
                "path": rel.as_posix(),
                "category": category(rel),
                "media_type": media_type(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )

    manifest = {
        **metadata,
        "file_count": len(entries),
        "checksum_algorithm": "SHA-256",
        "files": entries,
    }
    return manifest, [entry["path"] for entry in entries]


def validate_manifest(manifest: dict, schema_path: Path) -> list[str]:
    schema = load_json(schema_path)
    Draft202012Validator.check_schema(schema)
    errors = sorted(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(manifest),
        key=lambda error: list(error.absolute_path),
    )
    return [
        f"{'/'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
        for error in errors
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build manifest.json and manifest.sha256 for a package"
    )
    parser.add_argument("package", type=Path, help="Package directory")
    parser.add_argument(
        "--schema",
        type=Path,
        help="Schema path; defaults to PACKAGE/Documentation/manifest.schema.json",
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        help="Optional JSON file overriding package metadata",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print only; do not write files"
    )
    parser.add_argument(
        "--json", action="store_true", dest="json_output", help="JSON result"
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Re-read generated files and validate checksum after writing",
    )
    args = parser.parse_args()

    report = {
        "tool": "build_manifest.py",
        "tool_version": "1.0.0",
        "package": str(args.package.resolve()),
        "result": "FAIL",
        "exit_code": EXIT["INTERNAL"],
        "files": [],
        "errors": [],
    }

    try:
        root = args.package.resolve()
        if not root.is_dir():
            report["errors"].append("Package directory not found")
            report["exit_code"] = EXIT["PACKAGE_MISSING"]
            return finish(report, args.json_output)

        schema_path = (
            args.schema.resolve()
            if args.schema
            else root / "Documentation" / "manifest.schema.json"
        )
        if not schema_path.is_file():
            report["errors"].append(f"Schema not found: {schema_path}")
            report["exit_code"] = EXIT["SCHEMA_MISSING"]
            return finish(report, args.json_output)

        try:
            manifest, files = build_manifest(root, args.metadata)
        except json.JSONDecodeError as exc:
            report["errors"].append(f"Invalid JSON: {exc}")
            report["exit_code"] = EXIT["JSON_ERROR"]
            return finish(report, args.json_output)
        except RuntimeError as exc:
            report["errors"].append(str(exc))
            report["exit_code"] = EXIT["NO_FILES"]
            return finish(report, args.json_output)

        validation_errors = validate_manifest(manifest, schema_path)
        if validation_errors:
            report["errors"].extend(validation_errors)
            report["exit_code"] = EXIT["SCHEMA_FAIL"]
            return finish(report, args.json_output)

        manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
        report["files"] = files
        report["file_count"] = len(files)

        if not args.dry_run:
            manifest_path = root / "manifest.json"
            checksum_path = root / "Documentation" / "manifest.sha256"
            atomic_write(manifest_path, manifest_text)
            atomic_write(
                checksum_path, f"{sha256(manifest_path)}  manifest.json\n"
            )

            if args.validate:
                rebuilt = load_json(manifest_path)
                recheck = validate_manifest(rebuilt, schema_path)
                expected = checksum_path.read_text(encoding="utf-8").split()[0]
                actual = sha256(manifest_path)
                if recheck or expected != actual:
                    report["errors"].extend(recheck)
                    if expected != actual:
                        report["errors"].append("manifest.sha256 mismatch")
                    report["exit_code"] = EXIT["INTERNAL"]
                    return finish(report, args.json_output)
        else:
            report["manifest_preview"] = manifest

        report["result"] = "PASS"
        report["exit_code"] = EXIT["PASS"]
        return finish(report, args.json_output)

    except Exception as exc:
        report["errors"].append(f"{type(exc).__name__}: {exc}")
        return finish(report, args.json_output)


def finish(report: dict, as_json: bool) -> int:
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Package: {report['package']}")
        print(f"Files: {report.get('file_count', 0)}")
        for error in report["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"RESULT: {report['result']} (exit {report['exit_code']})")
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
