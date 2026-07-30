"""Generate deterministic DOCX packages for guided ontology contributions."""

from __future__ import annotations

import hashlib
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

TEMPLATE_VERSION = "2"
LAYOUT_VERSION = "2"
IKG_VERSION = "0.1.0"
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
NODE_LIMITS = {"selected": 1, "10": 10, "25": 25, "50": 50, "all": None}
CONTRIBUTION_LABELS = {
    "description": "Correzione o ampliamento",
    "source": "Nuova fonte",
    "synonyms": "Nuovi sinonimi",
    "notes": "Nuove note",
    "relationships": "Nuove relazioni",
    "new_concepts": "Nuovi concetti",
    "complete_review": "Revisione",
    "custom": "Personalizzato",
}


class GuidedContributionError(ValueError):
    """Raised when a guided package request is invalid."""


@dataclass(frozen=True, slots=True)
class GuidedSelection:
    domain_id: str
    area_id: str | None = None
    subarea_id: str | None = None
    node_id: str | None = None
    fields: tuple[str, ...] = ()
    node_limit: str = "10"


class GuidedContributionService:
    """Create Word-editable contribution templates from the working ontology."""

    def __init__(self, store: OntologyStore, repository_root: Path) -> None:
        self.store = store
        self.output_dir = repository_root / "contributions"
        self.generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    def options(self) -> dict[str, object]:
        return {
            "tree": self.store.tree(),
            "fields": list(FIELDS),
            "node_limits": list(NODE_LIMITS),
        }

    def _ordered_branch(self, selection: GuidedSelection) -> list[dict[str, object]]:
        nodes = self.store._all_nodes()
        by_id = {node["id"]: node for node in nodes}
        selected_id = (
            selection.node_id or selection.subarea_id or selection.area_id or selection.domain_id
        )
        if selected_id not in by_id:
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

        children: dict[str, list[dict[str, object]]] = {}
        for node in nodes:
            parent_id = node.get("parent_id")
            if isinstance(parent_id, str):
                children.setdefault(parent_id, []).append(node)
        for siblings in children.values():
            siblings.sort(key=self.store._ui_sort_key)

        ordered: list[dict[str, object]] = []

        def visit(node: dict[str, object]) -> None:
            ordered.append(node)
            for child in children.get(str(node["id"]), []):
                visit(child)

        visit(by_id[selected_id])
        return ordered

    def _selection_nodes(self, selection: GuidedSelection) -> tuple[list[dict[str, object]], int]:
        if selection.node_limit not in NODE_LIMITS:
            raise GuidedContributionError(f"Invalid node limit: {selection.node_limit}")
        branch = self._ordered_branch(selection)
        limit = NODE_LIMITS[selection.node_limit]
        included = branch if limit is None else branch[:limit]
        return included, len(branch)

    def preview(self, selection: GuidedSelection) -> dict[str, object]:
        unknown = sorted(set(selection.fields) - set(FIELDS))
        if unknown or not selection.fields:
            raise GuidedContributionError(
                f"Invalid contribution fields: {', '.join(unknown) or 'none selected'}"
            )
        nodes, total_nodes = self._selection_nodes(selection)
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
            "included_nodes": len(nodes),
            "excluded_nodes": total_nodes - len(nodes),
            "total_nodes": total_nodes,
            "fields": field_count,
            "estimated_minutes": minutes,
            "requested_fields": list(selection.fields),
            "requested_node_limit": selection.node_limit,
            "included_node_ids": [str(node["id"]) for node in nodes],
        }

    @staticmethod
    def _run(text: object, *, bold: bool = False, size: int = 22, hidden: bool = False) -> str:
        flags = ("<w:b/>" if bold else "") + ("<w:vanish/>" if hidden else "")
        return (
            f'<w:r><w:rPr>{flags}<w:sz w:val="{size}"/></w:rPr>'
            f'<w:t xml:space="preserve">{escape(str(text or ""))}</w:t></w:r>'
        )

    @classmethod
    def _paragraph(
        cls,
        text: object,
        *,
        bold: bool = False,
        size: int = 22,
        keep_next: bool = False,
        page_break_before: bool = False,
        hidden: bool = False,
    ) -> str:
        properties = (
            "<w:pPr>"
            + ("<w:keepNext/>" if keep_next else "")
            + ("<w:pageBreakBefore/>" if page_break_before else "")
            + '<w:spacing w:after="120"/>'
            + "</w:pPr>"
        )
        return f"<w:p>{properties}{cls._run(text, bold=bold, size=size, hidden=hidden)}</w:p>"

    @classmethod
    def _card_row(
        cls,
        label: str,
        value: object = "",
        *,
        protected: bool,
        height: int = 0,
    ) -> str:
        fill = "E2F0D9" if protected else "FFF2CC"
        status = "Protetto" if protected else "Da compilare"
        height_xml = f'<w:trHeight w:val="{height}" w:hRule="atLeast"/>' if height else ""
        return (
            f"<w:tr><w:trPr><w:cantSplit/>{height_xml}</w:trPr>"
            '<w:tc><w:tcPr><w:tcW w:w="2700" w:type="dxa"/>'
            f'<w:shd w:fill="{fill}"/></w:tcPr>'
            f"{cls._paragraph(label, bold=True, keep_next=True)}"
            f"{cls._paragraph(status, size=18)}</w:tc>"
            '<w:tc><w:tcPr><w:tcW w:w="6500" w:type="dxa"/>'
            f'<w:shd w:fill="{fill}"/></w:tcPr>{cls._paragraph(value)}</w:tc></w:tr>'
        )

    @classmethod
    def _card(
        cls,
        marker: str,
        title: str,
        rows: tuple[tuple[str, object, bool, int], ...],
        *,
        page_break_before: bool = False,
    ) -> str:
        title_row = (
            "<w:tr><w:trPr><w:cantSplit/></w:trPr><w:tc>"
            '<w:tcPr><w:gridSpan w:val="2"/><w:shd w:fill="D9EAF7"/></w:tcPr>'
            f"{cls._paragraph(marker, hidden=True)}"
            f"{cls._paragraph(title, bold=True, size=28, keep_next=True)}</w:tc></w:tr>"
        )
        body = "".join(
            cls._card_row(label, value, protected=protected, height=height)
            for label, value, protected, height in rows
        )
        prefix = cls._paragraph("", page_break_before=True) if page_break_before else ""
        return (
            f'{prefix}<w:tbl><w:tblPr><w:tblW w:w="9200" w:type="dxa"/>'
            '<w:tblBorders><w:top w:val="single" w:sz="8" w:color="666666"/>'
            '<w:left w:val="single" w:sz="8" w:color="666666"/>'
            '<w:bottom w:val="single" w:sz="8" w:color="666666"/>'
            '<w:right w:val="single" w:sz="8" w:color="666666"/>'
            '<w:insideH w:val="single" w:sz="4" w:color="AAAAAA"/>'
            '<w:insideV w:val="single" w:sz="4" w:color="AAAAAA"/>'
            f"</w:tblBorders></w:tblPr>{title_row}{body}</w:tbl>"
            f"{cls._paragraph('')}"
        )

    @classmethod
    def _node_card(cls, node: dict[str, object], *, page_break_before: bool) -> str:
        rows = (
            ("ID", node["id"], True, 0),
            ("Tipo", node["type"], True, 0),
            ("Parent", node.get("parent_id") or "null", True, 0),
            ("Label", node["label"], True, 0),
            ("Lingua", node.get("language") or "it", True, 0),
            ("Descrizione esistente", node["description"], True, 700),
            ("Nuova descrizione o proposta di correzione", "", False, 1100),
            ("Fonte", "", False, 650),
            ("Sinonimi", "", False, 650),
            ("Note e osservazioni", "", False, 1100),
            ("Nuove relazioni proposte", "", False, 650),
        )
        return cls._card(
            "IKG_NODE_CARD_V2",
            str(node["label"]),
            rows,
            page_break_before=page_break_before,
        )

    @classmethod
    def _new_node_card(cls, number: int) -> str:
        rows = (
            ("Parent proposto", "", False, 600),
            ("ID proposto", "", False, 600),
            ("Tipo proposto", "", False, 600),
            ("Label", "", False, 600),
            ("Descrizione", "", False, 1100),
            ("Fonte", "", False, 600),
            ("Sinonimi", "", False, 600),
            ("Note", "", False, 900),
            ("Relazioni proposte", "", False, 600),
        )
        return cls._card(
            "IKG_NEW_NODE_CARD_V2",
            f"Nuova voce proposta {number}",
            rows,
            page_break_before=number > 1,
        )

    def _document(
        self,
        preview: dict[str, object],
        nodes: list[dict[str, object]],
        contribution_id: str,
    ) -> bytes:
        selected = set(preview["requested_fields"])
        contribution_types = [
            self._paragraph(
                f"{'☒' if field in selected else '☐'} {label}",
                size=21,
            )
            for field, label in CONTRIBUTION_LABELS.items()
        ]
        instructions = (
            "Non modificare gli ID esistenti.",
            "Non modificare Tipo o Parent dei nodi esistenti.",
            "Non modificare la gerarchia esistente.",
            "Compila liberamente i campi indicati come Da compilare.",
            'Usa "Nuovi concetti o nuove voci proposte" per aggiungere contenuti.',
            "Salva il documento in formato DOCX.",
            'Reimportalo mediante "Importa Ontologia".',
        )
        content = [
            self._paragraph("Italian Knowledge Graph", bold=True, size=36, keep_next=True),
            self._paragraph("Richiesta di contributo", bold=True, size=32, keep_next=True),
            self._paragraph(
                "Abbiamo bisogno della tua competenza per migliorare questa parte della "
                "conoscenza. Compila soltanto i campi sui quali desideri contribuire."
            ),
            self._paragraph(f"Identificativo: {contribution_id}"),
            self._paragraph(f"Dominio: {preview['domain']}"),
            self._paragraph(f"Area: {preview['area'] or '-'}"),
            self._paragraph(f"Sottoarea: {preview['subarea'] or '-'}"),
            self._paragraph(f"Nodo: {preview['node'] or '-'}"),
            self._paragraph(f"Numero elementi: {preview['included_nodes']}"),
            self._paragraph(f"Tempo stimato: {preview['estimated_minutes']} minuti"),
            self._paragraph(f"Versione template: {TEMPLATE_VERSION}"),
            self._paragraph(f"Data di generazione: {self.generated_at}"),
            self._paragraph("Tipo di contributo", bold=True, size=26, keep_next=True),
            *contribution_types,
            self._paragraph("Istruzioni", bold=True, size=26, keep_next=True),
            *(self._paragraph(f"• {instruction}") for instruction in instructions),
            self._paragraph("Schede dei nodi", bold=True, size=30, page_break_before=True),
        ]
        content.extend(
            self._node_card(node, page_break_before=index > 0 and index % 2 == 0)
            for index, node in enumerate(nodes)
        )
        if "new_concepts" in selected:
            content.append(
                self._paragraph(
                    "Nuovi concetti o nuove voci proposte",
                    bold=True,
                    size=30,
                    page_break_before=True,
                )
            )
            content.extend(self._new_node_card(number) for number in range(1, 4))
        document = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            f"<w:body>{''.join(content)}"
            '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1134" w:right="1134" w:bottom="1134" w:left="1134"'
            ' w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>'
            "</w:body></w:document>"
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

    def _snapshot_identifier(self) -> str:
        serialized = json.dumps(
            self.store.snapshot(),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()

    def _contribution_id(self, selection: GuidedSelection, snapshot: str) -> str:
        payload = {
            "domain_id": selection.domain_id,
            "area_id": selection.area_id,
            "subarea_id": selection.subarea_id,
            "node_id": selection.node_id,
            "fields": selection.fields,
            "node_limit": selection.node_limit,
            "snapshot": snapshot,
        }
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()
        return f"ikg-{digest[:16]}"

    def create(
        self,
        selection: GuidedSelection,
        filename: str = "ikg-guided-contribution.zip",
    ) -> dict[str, object]:
        if Path(filename).name != filename or not filename.lower().endswith(".zip"):
            raise GuidedContributionError("Package filename must be a safe .zip name")
        preview = self.preview(selection)
        nodes, _ = self._selection_nodes(selection)
        snapshot = self._snapshot_identifier()
        contribution_id = self._contribution_id(selection, snapshot)
        metadata = {
            "contribution_id": contribution_id,
            "template_version": TEMPLATE_VERSION,
            "layout_version": LAYOUT_VERSION,
            "generated_at": self.generated_at,
            "selected_domain": selection.domain_id,
            "selected_area": selection.area_id,
            "selected_subarea": selection.subarea_id,
            "selected_node": selection.node_id,
            "selected_contribution_types": preview["requested_fields"],
            "requested_node_limit": preview["requested_node_limit"],
            "included_node_ids": preview["included_node_ids"],
            "excluded_node_count": preview["excluded_nodes"],
            "canonical_snapshot": snapshot,
            "ikg_version": IKG_VERSION,
            "node_count": preview["included_nodes"],
            "import_file": "contribution.docx",
            "domain": preview["domain"],
            "area": preview["area"],
            "subarea": preview["subarea"],
            "generated_on": self.generated_at[:10],
            "requested_fields": preview["requested_fields"],
        }
        readme = (
            b"ITALIAN KNOWLEDGE GRAPH - RICHIESTA DI CONTRIBUTO\n\n"
            b"1. Apri contribution.docx.\n"
            b"2. Scegli liberamente quali campi compilare.\n"
            b"3. Non modificare i dati indicati come Protetto.\n"
            b'4. Usa "Nuovi concetti o nuove voci proposte" per aggiungere contenuti.\n'
            b"5. Salva il documento in formato DOCX.\n"
            b"6. Restituisci il pacchetto o reimporta il documento mediante "
            b'"Importa Ontologia".\n'
            b"7. Tutte le proposte saranno sottoposte a Preview, revisione e Validator.\n"
        )
        docx = self._docx(self._document(preview, nodes, contribution_id))
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
            "contribution_id": contribution_id,
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
