"""Persistent external-to-canonical type mappings."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

CANONICAL_TYPES = frozenset({"macroarea", "area", "sottoarea"})
DEFAULT_MAPPINGS = {
    "categoria": "sottoarea",
    "subarea": "sottoarea",
}


class MappingError(ValueError):
    """Raised when a mapping configuration is invalid."""


class MappingEngine:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path

    @staticmethod
    def _validate(mappings: dict[str, str]) -> dict[str, str]:
        normalized: dict[str, str] = {}
        for external_type, canonical_type in mappings.items():
            if not isinstance(external_type, str) or not external_type.strip():
                raise MappingError("External mapping types must be non-empty strings")
            if canonical_type not in CANONICAL_TYPES:
                raise MappingError(
                    f"Invalid canonical mapping target {canonical_type!r} for {external_type!r}"
                )
            normalized[external_type.casefold()] = canonical_type
        return normalized

    def load(self) -> dict[str, str]:
        mappings = dict(DEFAULT_MAPPINGS)
        if self.path is None or not self.path.exists():
            return mappings
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise MappingError(f"Cannot load mapping configuration: {exc}") from exc
        if not isinstance(payload, dict):
            raise MappingError("Mapping configuration must be a JSON object")
        if not all(
            isinstance(key, str) and isinstance(value, str) for key, value in payload.items()
        ):
            raise MappingError("Mapping configuration entries must be strings")
        mappings.update(self._validate(payload))
        return mappings

    def resolve(
        self,
        external_type: str,
        overrides: dict[str, str] | None = None,
    ) -> str | None:
        normalized = external_type.casefold()
        if normalized in CANONICAL_TYPES:
            return normalized
        mappings = self.load()
        if overrides:
            mappings.update(self._validate(overrides))
        return mappings.get(normalized)

    def save(self, mappings: dict[str, str]) -> None:
        if self.path is None:
            raise MappingError("No persistent mapping path is configured")
        merged = self.load()
        merged.update(self._validate(mappings))
        content = json.dumps(dict(sorted(merged.items())), ensure_ascii=False, indent=2) + "\n"
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                newline="\n",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as handle:
                temporary = Path(handle.name)
                handle.write(content)
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
