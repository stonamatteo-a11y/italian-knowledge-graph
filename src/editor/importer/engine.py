"""Apply a previously validated import to the canonical store."""

from __future__ import annotations

from typing import Any, Protocol


class ImportStore(Protocol):
    def replace_and_save(self, records: dict[str, list[dict[str, Any]]]) -> None: ...


class ImportEngine:
    def apply(
        self,
        store: ImportStore,
        records: dict[str, list[dict[str, Any]]],
    ) -> None:
        store.replace_and_save(records)
