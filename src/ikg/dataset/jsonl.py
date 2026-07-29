"""Deterministic JSON Lines dataset exporter."""

from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from .exporter import record_mapping
from .models import DatasetRecord


class JsonlExporter:
    def export(self, records: Iterable[DatasetRecord], output: str | Path) -> None:
        lines = (
            json.dumps(record_mapping(record), ensure_ascii=False, separators=(",", ":"))
            for record in records
        )
        content = "\n".join(lines)
        if content:
            content += "\n"
        Path(output).write_text(content, encoding="utf-8", newline="\n")
