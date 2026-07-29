"""Build the user-facing import preview."""

from __future__ import annotations

from .models import ConversionResult, ImportPreview
from .validator import ImportValidation


class PreviewBuilder:
    def build(
        self,
        *,
        token: str | None,
        format_name: str,
        parser_name: str,
        nodes_found: int,
        relationships_found: int,
        conversion: ConversionResult,
        validation: ImportValidation,
    ) -> ImportPreview:
        errors = tuple(sorted({*conversion.errors, *validation.errors}))
        warnings = tuple(sorted(conversion.warnings))
        return ImportPreview(
            token if not errors else None,
            format_name,
            parser_name,
            nodes_found,
            relationships_found,
            validation.nodes_to_add,
            conversion.modifications,
            validation.collisions,
            validation.duplicates,
            warnings,
            tuple((f"warning-{index + 1}", warning) for index, warning in enumerate(warnings)),
            (
                f"Parser selected: {parser_name}",
                f"Canonical candidates: {len(conversion.nodes)}",
                f"Existing duplicates skipped: {len(validation.duplicates)}",
            ),
            conversion.unmapped_types,
            errors,
        )
