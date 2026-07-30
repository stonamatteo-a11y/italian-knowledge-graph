"""Orchestrate parsing, conversion, validation, preview, and import."""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from pathlib import Path
from threading import RLock
from typing import Any, Protocol

from .converter import CanonicalConverter
from .engine import ImportEngine
from .mapping import MappingEngine, MappingError
from .models import ImportPreview, ImportReport
from .parsers import ImportParseError, ParserRegistry
from .preview import PreviewBuilder
from .validator import ImportValidation, ImportValidator


class ImportStore(Protocol):
    def snapshot(self) -> dict[str, list[dict[str, Any]]]: ...

    def replace_and_save(self, records: dict[str, list[dict[str, Any]]]) -> None: ...


@dataclass(frozen=True, slots=True)
class PendingImport:
    records: dict[str, list[dict[str, Any]]]
    nodes_to_add: int
    relationships_to_add: int
    filename: str
    format_name: str
    parser_name: str
    modifications: tuple[str, ...]
    warnings: tuple[tuple[str, str], ...]
    mapping_file_modified: bool


class ImportManager:
    def __init__(self, mapping_path: Path | None = None) -> None:
        self.parsers = ParserRegistry()
        self.mapping_engine = MappingEngine(mapping_path)
        self.converter = CanonicalConverter(self.mapping_engine)
        self.validator = ImportValidator()
        self.preview_builder = PreviewBuilder()
        self.engine = ImportEngine()
        self._pending: dict[str, PendingImport] = {}
        self._lock = RLock()

    def preview(
        self,
        store: ImportStore,
        filename: str,
        content: bytes | str,
        mode: str = "assisted",
        mappings: dict[str, str] | None = None,
        persist_mappings: bool = False,
    ) -> ImportPreview:
        if mode not in {"assisted", "automatic"}:
            return ImportPreview(
                token=None,
                format_name="unknown",
                parser_name="none",
                nodes_found=0,
                relationships_found=0,
                nodes_to_add=0,
                modifications=(),
                collisions=(),
                duplicates=(),
                warnings=(),
                warning_options=(),
                information=(),
                unmapped_types=(),
                errors=("Unsupported import mode",),
            )
        try:
            parsed = self.parsers.parse(filename, content)
        except ImportParseError as exc:
            return ImportPreview(
                token=None,
                format_name="unknown",
                parser_name="none",
                nodes_found=0,
                relationships_found=0,
                nodes_to_add=0,
                modifications=(),
                collisions=(),
                duplicates=(),
                warnings=(),
                warning_options=(),
                information=(),
                unmapped_types=(),
                errors=(str(exc),),
            )
        try:
            if persist_mappings and mappings:
                self.mapping_engine.save(mappings)
            converted = self.converter.convert(parsed, mappings)
        except MappingError as exc:
            return ImportPreview(
                token=None,
                format_name=parsed.format_name,
                parser_name=parsed.parser_name,
                nodes_found=len(parsed.nodes),
                relationships_found=sum(node.parent is not None for node in parsed.nodes),
                nodes_to_add=0,
                modifications=(),
                collisions=(),
                duplicates=(),
                warnings=(),
                warning_options=(),
                information=(),
                unmapped_types=(),
                errors=(str(exc),),
            )
        validation = (
            ImportValidation(None, 0, 0, (), (), (), ())
            if converted.unmapped_types
            else self.validator.validate(store.snapshot(), converted.nodes)
        )
        errors = {*converted.errors, *validation.errors}
        warnings = tuple(sorted(converted.warnings))
        warning_options = tuple(
            (f"warning-{index + 1}", warning) for index, warning in enumerate(warnings)
        )
        token = None
        if not errors and not converted.unmapped_types and validation.records is not None:
            token = secrets.token_urlsafe(24)
            with self._lock:
                self._pending[token] = PendingImport(
                    validation.records,
                    validation.nodes_to_add,
                    validation.relationships_to_add,
                    filename,
                    parsed.format_name,
                    parsed.parser_name,
                    converted.modifications,
                    warning_options,
                    persist_mappings and bool(mappings),
                )
        return self.preview_builder.build(
            token=token,
            format_name=parsed.format_name,
            parser_name=parsed.parser_name,
            nodes_found=len(parsed.nodes),
            relationships_found=sum(node.parent is not None for node in parsed.nodes),
            conversion=converted,
            validation=validation,
        )

    def preview_path(
        self,
        store: ImportStore,
        path: Path,
        mode: str = "assisted",
        mappings: dict[str, str] | None = None,
        persist_mappings: bool = False,
    ) -> ImportPreview:
        """Preview a local file using its original binary stream."""
        with path.open("rb") as stream:
            return self.preview(
                store,
                path.name,
                stream.read(),
                mode,
                mappings,
                persist_mappings,
            )

    def confirm(
        self,
        store: ImportStore,
        token: str,
        accepted_warnings: tuple[str, ...] = (),
    ) -> ImportReport:
        with self._lock:
            pending = self._pending.get(token)
        if pending is None:
            raise KeyError(token)
        required = {identifier for identifier, _ in pending.warnings}
        missing = required - set(accepted_warnings)
        if missing:
            raise ValueError("All data-loss warnings must be acknowledged")
        with self._lock:
            self._pending.pop(token, None)
        self.engine.apply(store, pending.records)
        handled = tuple(
            message for identifier, message in pending.warnings if identifier in required
        )
        files_modified = [
            "ontology/macroareas.json",
            "ontology/areas.json",
            "ontology/subareas.json",
            "ontology/seed_compressed.py",
        ]
        if pending.mapping_file_modified:
            files_modified.append("ontology/import_mappings.json")
        return ImportReport(
            pending.filename,
            pending.format_name,
            pending.parser_name,
            pending.modifications,
            handled,
            (),
            tuple(files_modified),
            pending.nodes_to_add,
            pending.relationships_to_add,
        )
