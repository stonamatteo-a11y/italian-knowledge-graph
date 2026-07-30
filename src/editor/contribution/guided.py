"""Generate deterministic DOCX packages for guided ontology contributions."""

from __future__ import annotations

import io
import json
import os
import tempfile
import webbrowser
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape

from ..store import OntologyStore
from .service import ZIP_TIMESTAMP

TEMPLATE_VERSION = "1"
IKG_VERSION = "1"
FIELDS = (
    "description",
    "source",
    "synonyms",
    "notes",
    "relationships",
    "new_concepts",
    "complete_review",
    "custom",
)
HEADERS = ("ID", "Type", "Parent", "Label", "Description", "Source", "Synonyms", "Notes")


class GuidedContributionError(ValueError):
    """Raised when a guided package request is invalid."""


@dataclass(frozen=True, slots=True)
class GuidedSelection:
    domain_id: str
    area_id: str | None = None
    subarea_id: str | None = None
    node_id: str | None = None
    fields: tuple[str, ...] = ()


class GuidedContributionService:
    """Create Word-editable contribution templates from the working ontology."""

    def __init__(self, store: OntologyStore, repository_root: Path) -> None:
        self.store = store
        self.output_dir = repository_root / "contributions"

    def options(self) -> dict[str, object]:
        return {"tree": self.store.tree(), "fields": list(FIELDS)}

    def _selected_nodes(self, selection: GuidedSelection) -> list[dict[str, object]]:
        nodes = self.store._all_nodes()
        by_id = {node["id"]: node for node in nodes}
        selected_id = (
            selection.node_id or selection.subarea_id or selection.area_id or selection.domain_id
        )
        selected = by_id.get(selected_id)
        if selected is None:
            raise GuidedContributionError(f"Unknown selected node: {selected_id}")
        if selection.domain_id not in by_id or by_id[selection.domain_id]["type"] != "macroarea":
            raise GuidedContributionError("A valid domain is required")
        expected_parent = selection.domain_id
        for node_id in (selection.area_id, selection.subarea_id, selection.node_id):
            if node_id is None:
                continue
            if node_id not in by_id or by_id[node_id].get("parent_id") != expected_parent:
                raise GuidedContributionError("The selected hierarchy is inconsistent")
            expected_parent = node_id
        descendants = {selected_id}
        changed = True
        while changed:
            changed = False
            for node in nodes:
                if node.get("parent_id") in descendants and node["id"] not in descendants:
                    descendants.add(node["id"])
                    changed = True
        return [node for node in nodes if node["id"] in descendants]

    def preview(self, selection: GuidedSelection) -> dict[str, object]:
        unknown = sorted(set(selection.fields) - set(FIELDS))
        if unknown or not selection.fields:
            raise GuidedContributionError(
                f"Invalid contribution fields: {', '.join(unknown) or 'none selected'}"
            )
        nodes = self._selected_nodes(selection)
        requested = set(selection.fields)
        editable = requested & {"description", "source", "synonyms", "notes", "relationships"}
        if "complete_review" in requested:
            editable.update(("description", "source", "synonyms", "notes", "relationships"))
        field_count = len(nodes) * len(editable)
        minutes = max(5, ((field_count * 2 + 4) // 5) * 5)
        by_id = {node["id"]: node for node in self.store._all_nodes()}
        return {
            "domain": by_id[selection.domain_id]["label"],
            "area": by_id[selection.area_id]["label"] if selection.area_id else None,
            "subarea": by_id[selection.subarea_id]["label"] if selection.subarea_id else None,
            "node": by_id[selection.node_id]["label"] if selection.node_id else None,
            "nodes": len(nodes),
            "fields": field_count,
            "estimated_minutes": minutes,
            "requested_fields": list(selection.fields),
        }

    @staticmethod
    def _paragraph(text: str, *, bold: bool = False) -> str:
        properties = "<w:rPr><w:b/></w:rPr>" if bold else ""
        return f"<w:p><w:r>{properties}<w:t>{escape(text)}</w:t></w:r></w:p>"

    @staticmethod
    def _cell(value: object, *, filled: bool = False) -> str:
        fill = "E2F0D9" if filled else "FFF2CC"
        shade = f'<w:tcPr><w:shd w:fill="{fill}"/></w:tcPr>'
        return (
            f'<w:tc>{shade}<w:p><w:r><w:t xml:space="preserve">'
            f"{escape(str(value or ''))}</w:t></w:r></w:p></w:tc>"
        )

    def _table(self, nodes: list[dict[str, object]]) -> str:
        header = "<w:tr>" + "".join(self._cell(value, filled=True) for value in HEADERS) + "</w:tr>"
        rows = []
        for node in nodes:
            values = (
                node["id"],
                node["type"],
                node.get("parent_id") or "null",
                node["label"],
                node["description"],
                "",
                "",
                "",
            )
            rows.append(
                "<w:tr>"
                + "".join(
                    self._cell(value, filled=index < 5 and bool(value))
                    for index, value in enumerate(values)
                )
                + "</w:tr>"
            )
        return "<w:tbl>" + header + "".join(rows) + "</w:tbl>"

    def _document(self, preview: dict[str, object], nodes: list[dict[str, object]]) -> bytes:
        intro = [
            self._paragraph("Italian Knowledge Graph", bold=True),
            self._paragraph("Contributo guidato", bold=True),
            self._paragraph(f"Dominio: {preview['domain']}"),
            self._paragraph(f"Area: {preview['area'] or '-'}"),
            self._paragraph(f"Sottoarea: {preview['subarea'] or '-'}"),
            self._paragraph(f"Numero elementi: {preview['nodes']}"),
            self._paragraph(f"Tempo stimato: {preview['estimated_minutes']} minuti"),
            self._paragraph("Non modificare ID, Type o Parent. Completa solo i campi richiesti."),
            self._table(nodes),
        ]
        if "new_concepts" in preview["requested_fields"]:
            intro.extend(
                (
                    self._paragraph("Nuovi concetti", bold=True),
                    self._table([]),
                )
            )
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{''.join(intro)}<w:sectPr/></w:body></w:document>"
        )
        return document.encode("utf-8")

    @staticmethod
    def _zip_entry(archive: zipfile.ZipFile, name: str, content: bytes) -> None:
        info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o100644 << 16
        archive.writestr(info, content, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)

    @staticmethod
    def _atomic_write(path: Path, content: bytes) -> None:
        fd, temporary_name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, path)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)

    def _docx(self, document: bytes) -> bytes:
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w") as archive:
            self._zip_entry(
                archive,
                "[Content_Types].xml",
                b'<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>',
            )
            self._zip_entry(
                archive,
                "_rels/.rels",
                b'<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>',
            )
            self._zip_entry(archive, "word/document.xml", document)
        return output.getvalue()

    def create(
        self,
        selection: GuidedSelection,
        filename: str = "ikg-guided-contribution.zip",
    ) -> dict[str, object]:
        if Path(filename).name != filename or not filename.lower().endswith(".zip"):
            raise GuidedContributionError("Package filename must be a safe .zip name")
        preview = self.preview(selection)
        nodes = self._selected_nodes(selection)
        metadata = {
            "ikg_version": IKG_VERSION,
            "template_version": TEMPLATE_VERSION,
            "domain": preview["domain"],
            "area": preview["area"],
            "subarea": preview["subarea"],
            "generated_on": datetime.now(timezone.utc).date().isoformat(),
            "node_count": preview["nodes"],
            "requested_fields": preview["requested_fields"],
            "import_file": "contribution.docx",
        }
        readme = (
            b"ITALIAN KNOWLEDGE GRAPH - CONTRIBUTO GUIDATO\n\n"
            b"Compila contribution.docx con Microsoft Word o software compatibile.\n"
            b"Non modificare ID, Type o Parent esistenti. Completa i campi richiesti e,\n"
            b"se previsto, aggiungi righe nella tabella Nuovi concetti.\n"
            b"Reimporta contribution.docx con il comando Importa Ontologia dell'editor IKG.\n"
        )
        docx = self._docx(self._document(preview, nodes))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        destination = self.output_dir / filename
        document_path = self.output_dir / f"{Path(filename).stem}.docx"
        fd, temporary_name = tempfile.mkstemp(dir=self.output_dir, suffix=".tmp")
        try:
            with os.fdopen(fd, "wb") as stream, zipfile.ZipFile(stream, "w") as archive:
                self._zip_entry(archive, "contribution.docx", docx)
                self._zip_entry(archive, "README.txt", readme)
                self._zip_entry(
                    archive,
                    "metadata.json",
                    (
                        json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
                    ).encode("utf-8"),
                )
            os.replace(temporary_name, destination)
            self._atomic_write(document_path, docx)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)
        return {
            "created": True,
            "path": str(destination),
            "document_path": str(document_path),
            "filename": filename,
            **preview,
        }

    def open_generated(self, filename: str, target: str) -> None:
        if Path(filename).name != filename or not filename.lower().endswith(".zip"):
            raise GuidedContributionError("Invalid generated package name")
        path = (
            self.output_dir
            if target == "folder"
            else self.output_dir / f"{Path(filename).stem}.docx"
        )
        if target not in {"folder", "document"} or not path.exists():
            raise GuidedContributionError("Generated contribution target does not exist")
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        else:
            webbrowser.open(path.resolve().as_uri())
