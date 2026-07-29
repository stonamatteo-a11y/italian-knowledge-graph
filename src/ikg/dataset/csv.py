"""Deterministic CSV dataset exporter."""

from __future__ import annotations

import csv
import json
from collections.abc import Iterable
from pathlib import Path

from .exporter import record_mapping
from .models import DatasetRecord

CSV_FIELDS = ("entity_id", "entity_type", "label", "parent", "relationships")


class CsvExporter:
    def export(self, records: Iterable[DatasetRecord], output: str | Path) -> None:
        with Path(output).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
            writer.writeheader()
            for record in records:
                row = record_mapping(record)
                row["relationships"] = json.dumps(
                    row["relationships"],
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                writer.writerow(row)
