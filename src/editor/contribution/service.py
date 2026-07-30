"""Prepare deterministic, reviewable ontology contributions."""

from __future__ import annotations

import copy
import difflib
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Protocol

from scripts.generate_seed import SeedGenerationError, render_seed_module, validate_canonical

from ..quality import KnowledgeQualityCenter
from ..store import LEVELS
from .git import GitInspector
from .models import ContributionChanges, ContributionPreview

CANONICAL_ARCHIVE_FILES = {
    "macroareas": "ontology/macroareas.json",
    "areas": "ontology/areas.json",
    "subareas": "ontology/subareas.json",
}
SAFE_PACKAGE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\.zip")
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)


class ContributionError(ValueError):
    """Raised when contribution preparation cannot proceed safely."""


class ContributionStore(Protocol):
    ontology_dir: Path
    seed_path: Path

    def snapshot(self) -> dict[str, list[dict[str, Any]]]: ...

    def initial_snapshot(self) -> dict[str, list[dict[str, Any]]]: ...

    def activity(self) -> tuple[dict[str, Any], ...]: ...

    def replace_and_save(self, records: dict[str, list[dict[str, Any]]]) -> None: ...

    def validate(self) -> Any: ...


def _json_content(records: list[dict[str, Any]]) -> str:
    return json.dumps(records, ensure_ascii=False, indent=2) + "\n"


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _nodes(records: dict[str, list[dict[str, Any]]]) -> dict[str, dict[str, Any]]:
    result = {}
    for section, node_type, _ in LEVELS:
        for record in records[section]:
            result[record["id"]] = {
                **record,
                "type": node_type,
                "parent_id": record.get("parent_id"),
            }
    return result


def _relations(nodes: dict[str, dict[str, Any]]) -> set[tuple[str, str]]:
    return {
        (node["parent_id"], node["id"])
        for node in nodes.values()
        if node.get("parent_id") is not None
    }


class ContributionService:
    def __init__(
        self,
        store: ContributionStore,
        quality_center: KnowledgeQualityCenter,
        repository_root: Path,
    ) -> None:
        self.store = store
        self.quality_center = quality_center
        self.repository_root = repository_root.resolve()
        self.output_dir = self.repository_root / "contributions"
        self.git = GitInspector(self.repository_root)
        self.initial_git_state = self.git.inspect()

    def changes(self) -> ContributionChanges:
        before = _nodes(self.store.initial_snapshot())
        after = _nodes(self.store.snapshot())
        before_ids = set(before)
        after_ids = set(after)
        common = before_ids & after_ids
        modified_relationships = tuple(
            sorted(
                (
                    identifier,
                    before[identifier]["parent_id"],
                    after[identifier]["parent_id"],
                )
                for identifier in common
                if before[identifier].get("parent_id")
                and after[identifier].get("parent_id")
                and before[identifier]["parent_id"] != after[identifier]["parent_id"]
            )
        )
        modified_targets = {target for target, _, _ in modified_relationships}
        return ContributionChanges(
            tuple(sorted(after_ids - before_ids)),
            tuple(
                sorted(
                    identifier for identifier in common if before[identifier] != after[identifier]
                )
            ),
            tuple(sorted(before_ids - after_ids)),
            tuple(
                sorted(
                    relation
                    for relation in _relations(after) - _relations(before)
                    if relation[1] not in modified_targets
                )
            ),
            modified_relationships,
            tuple(
                sorted(
                    relation
                    for relation in _relations(before) - _relations(after)
                    if relation[1] not in modified_targets
                )
            ),
        )

    def _affected_files(
        self,
        before: dict[str, list[dict[str, Any]]],
        after: dict[str, list[dict[str, Any]]],
    ) -> tuple[str, ...]:
        files = [
            CANONICAL_ARCHIVE_FILES[section]
            for section in CANONICAL_ARCHIVE_FILES
            if before[section] != after[section]
        ]
        if files:
            files.append("ontology/seed_compressed.py")
        return tuple(files)

    def _diff(
        self,
        before: dict[str, list[dict[str, Any]]],
        after: dict[str, list[dict[str, Any]]],
    ) -> str:
        output = []
        for section, archive_path in CANONICAL_ARCHIVE_FILES.items():
            if before[section] == after[section]:
                continue
            output.extend(
                difflib.unified_diff(
                    _json_content(before[section]).splitlines(keepends=True),
                    _json_content(after[section]).splitlines(keepends=True),
                    fromfile=f"a/{archive_path}",
                    tofile=f"b/{archive_path}",
                    lineterm="\n",
                )
            )
        return "".join(output)

    def _git_blockers(self, files: tuple[str, ...]) -> tuple[str, ...]:
        current = self.git.inspect()
        if not current.available:
            return ()
        allowed = set(files)
        generated_prefix = "contributions/"
        blockers = {
            path
            for path in self.initial_git_state.dirty_paths
            if not path.startswith(generated_prefix)
        }
        blockers.update(
            path
            for path in current.dirty_paths
            if path not in allowed and not path.startswith(generated_prefix)
        )
        blockers.update(self._canonical_disk_blockers(files))
        return tuple(sorted(blockers))

    def _canonical_disk_blockers(self, files: tuple[str, ...]) -> set[str]:
        initial = self.store.initial_snapshot()
        current = self.store.snapshot()
        blockers: set[str] = set()
        for section, archive_path in CANONICAL_ARCHIVE_FILES.items():
            if archive_path not in files:
                continue
            path = self.repository_root / archive_path
            try:
                disk = path.read_text(encoding="utf-8")
            except OSError:
                blockers.add(archive_path)
                continue
            allowed = {_json_content(initial[section]), _json_content(current[section])}
            if disk not in allowed:
                blockers.add(archive_path)
        seed_archive_path = "ontology/seed_compressed.py"
        if seed_archive_path in files:
            try:
                disk_seed = (self.repository_root / seed_archive_path).read_text(encoding="utf-8")
            except OSError:
                blockers.add(seed_archive_path)
            else:
                allowed_seeds = {
                    render_seed_module(initial),
                    render_seed_module(current),
                }
                if disk_seed not in allowed_seeds:
                    blockers.add(seed_archive_path)
        return blockers

    def preview(self) -> ContributionPreview:
        before = self.store.initial_snapshot()
        after = self.store.snapshot()
        changes = self.changes()
        errors: list[str] = []
        authoritative = self.store.validate()
        errors.extend(authoritative.errors)
        try:
            validate_canonical(copy.deepcopy(after))
            first_seed = render_seed_module(after)
            second_seed = render_seed_module(after)
            if first_seed != second_seed:
                errors.append("Generated seed is not deterministic")
            for section in CANONICAL_ARCHIVE_FILES:
                first_json = _json_content(after[section])
                second_json = _json_content(copy.deepcopy(after[section]))
                if first_json != second_json:
                    errors.append(f"{section} serialization is not deterministic")
        except SeedGenerationError as exc:
            errors.append(str(exc))

        quality_before = self.quality_center.evaluate(before)
        quality_after = self.quality_center.evaluate(after, self.store.activity())
        errors.extend(issue.detail for issue in quality_after.issues if issue.severity == "error")
        warnings = tuple(
            issue.as_dict() for issue in quality_after.issues if issue.severity == "warning"
        )
        files = self._affected_files(before, after)
        title = self._commit_title(changes)
        body = self._pull_request_body(changes, quality_before.score, quality_after.score)
        git_state = self.git.inspect()
        return ContributionPreview(
            changes,
            files,
            self._diff(before, after),
            tuple(sorted(set(errors))),
            warnings,
            quality_before.score,
            quality_after.score,
            changes.nodes_removed,
            git_state.available,
            self._git_blockers(files),
            title,
            body,
        )

    @staticmethod
    def _commit_title(changes: ContributionChanges) -> str:
        node_count = (
            len(changes.nodes_added) + len(changes.nodes_modified) + len(changes.nodes_removed)
        )
        return f"feat: update ontology knowledge ({node_count} nodes)"

    @staticmethod
    def _pull_request_body(
        changes: ContributionChanges,
        quality_before: float,
        quality_after: float,
    ) -> str:
        return "\n".join(
            (
                "## Summary",
                "",
                f"- Added nodes: {len(changes.nodes_added)}",
                f"- Modified nodes: {len(changes.nodes_modified)}",
                f"- Removed nodes: {len(changes.nodes_removed)}",
                f"- Added relationships: {len(changes.relationships_added)}",
                f"- Modified relationships: {len(changes.relationships_modified)}",
                f"- Removed relationships: {len(changes.relationships_removed)}",
                f"- Quality score: {quality_before} → {quality_after}",
                "",
                "## Validation",
                "",
                "- Authoritative validator passed",
                "- Deterministic canonical generation verified",
            )
        )

    @staticmethod
    def _accepted_warnings(
        preview: ContributionPreview,
        accepted_warning_ids: tuple[str, ...],
    ) -> tuple[dict[str, Any], ...]:
        required = {str(warning["id"]) for warning in preview.warnings}
        missing = required - set(accepted_warning_ids)
        if missing:
            raise ContributionError("All contribution warnings must be accepted explicitly")
        return tuple(warning for warning in preview.warnings if warning["id"] in required)

    def _assert_preparable(
        self,
        preview: ContributionPreview,
        accepted_warning_ids: tuple[str, ...],
    ) -> tuple[dict[str, Any], ...]:
        if not preview.changes.changed:
            raise ContributionError("There are no session changes to contribute")
        if preview.errors:
            raise ContributionError("Contribution contains blocking validation errors")
        return self._accepted_warnings(preview, accepted_warning_ids)

    @staticmethod
    def _zip_entry(archive: zipfile.ZipFile, name: str, content: bytes) -> None:
        if name.startswith("/") or ".." in Path(name).parts:
            raise ContributionError(f"Unsafe archive path: {name}")
        info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    def export_package(
        self,
        filename: str,
        accepted_warning_ids: tuple[str, ...],
    ) -> dict[str, object]:
        if SAFE_PACKAGE_NAME.fullmatch(filename) is None:
            raise ContributionError("Package filename must be a safe .zip name")
        destination = (self.output_dir / filename).resolve()
        if destination.parent != self.output_dir.resolve():
            raise ContributionError("Package path escapes the authorized directory")
        preview = self.preview()
        accepted = self._assert_preparable(preview, accepted_warning_ids)
        records = self.store.snapshot()
        validation_report = {
            "valid": not preview.errors,
            "errors": list(preview.errors),
            "warnings_accepted": list(accepted),
        }
        quality_report = {
            "before": self.quality_center.evaluate(self.store.initial_snapshot()).as_dict(),
            "after": self.quality_center.evaluate(records, self.store.activity()).as_dict(),
        }
        contribution = {
            "schema_version": 1,
            "changes": preview.changes.as_dict(),
            "files": list(preview.files),
            "excluded": list(preview.excluded),
            "quality": {"before": preview.quality_before, "after": preview.quality_after},
            "commit_title": preview.commit_title,
            "pull_request_body": preview.pull_request_body,
        }
        entries: dict[str, bytes] = {
            "contribution.json": _json_bytes(contribution),
            "validation-report.json": _json_bytes(validation_report),
            "quality-report.json": _json_bytes(quality_report),
            "CHANGELOG.md": (
                f"# Contribution\n\n{preview.commit_title}\n\n"
                f"Quality score: {preview.quality_before} -> {preview.quality_after}\n"
            ).encode(),
            "README.txt": (
                b"Review contribution.json and the validation and quality reports.\n"
                b"Copy only reviewed ontology JSON files into the repository, run the Validator,\n"
                b"and submit the change through the normal pull request workflow.\n"
            ),
        }
        for section, archive_path in CANONICAL_ARCHIVE_FILES.items():
            if archive_path in preview.files:
                entries[archive_path] = _json_content(records[section]).encode("utf-8")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=self.output_dir,
                prefix=f".{filename}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
            with zipfile.ZipFile(temporary, "w") as archive:
                for name in sorted(entries):
                    self._zip_entry(archive, name, entries[name])
            os.replace(temporary, destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
        return self._final_report(
            "package", preview, accepted, str(Path("contributions") / filename)
        )

    def prepare_git(
        self,
        accepted_warning_ids: tuple[str, ...],
    ) -> dict[str, object]:
        preview = self.preview()
        accepted = self._assert_preparable(preview, accepted_warning_ids)
        if not preview.git_available:
            raise ContributionError("The editor is not running inside a Git repository")
        if preview.git_blockers:
            raise ContributionError(
                "Pre-existing Git changes block preparation: " + ", ".join(preview.git_blockers)
            )
        self.store.replace_and_save(self.store.snapshot())
        return self._final_report("git", preview, accepted, list(preview.files))

    @staticmethod
    def _final_report(
        mode: str,
        preview: ContributionPreview,
        accepted: tuple[dict[str, Any], ...],
        output: str | list[str],
    ) -> dict[str, object]:
        return {
            "mode": mode,
            "output": output,
            "changes": preview.changes.as_dict(),
            "validation": {"valid": not preview.errors, "errors": list(preview.errors)},
            "warnings_accepted": list(accepted),
            "quality": {"before": preview.quality_before, "after": preview.quality_after},
            "commit_title": preview.commit_title,
            "pull_request_body": preview.pull_request_body,
            "diff": preview.diff,
        }
