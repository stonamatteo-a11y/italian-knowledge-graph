"""Source-format parsers without dependencies on the IKG data model."""

from __future__ import annotations

import ast
import io
import json
import re
import zipfile
from typing import Any, ClassVar, Protocol
from xml.etree import ElementTree

from .models import ParsedOntology, SourceNode

KNOWN_FIELDS = {"id", "type", "label", "description", "parent", "parent_id", "language"}
KIMI_ARGUMENTS = (
    "id",
    "label",
    "description",
    "parent",
    "type",
    "keywords",
    "sinonimi",
    "termini_correlati",
    "prerequisiti",
    "concetti_collegati",
    "esempi",
    "livello_scolastico",
    "livello_difficolta",
    "fonti_consigliate",
)


class ImportParseError(ValueError):
    """Raised when no parser can safely read an import."""


class OntologyParser(Protocol):
    name: str

    def accepts(self, filename: str, content: bytes) -> bool: ...

    def parse(self, content: bytes) -> ParsedOntology: ...


def _source_node(record: dict[str, Any]) -> SourceNode:
    return SourceNode(
        identifier=record.get("id"),
        node_type=record.get("type"),
        label=record.get("label"),
        description=record.get("description"),
        parent=record.get("parent_id", record.get("parent")),
        language=record.get("language", "it"),
        extra_fields=tuple(sorted(set(record) - KNOWN_FIELDS)),
    )


class JsonOntologyParser:
    name = "json"

    def accepts(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".json") or content.lstrip().startswith((b"{", b"["))

    def parse(self, content: bytes) -> ParsedOntology:
        try:
            payload = json.loads(content.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            if isinstance(exc, json.JSONDecodeError):
                detail = f"{exc.msg} at line {exc.lineno}"
            else:
                detail = "file is not UTF-8"
            raise ImportParseError(f"Invalid JSON: {detail}") from exc
            raise ImportParseError(f"Invalid JSON: {exc.msg} at line {exc.lineno}") from exc

        if isinstance(payload, list):
            records = payload
        elif isinstance(payload, dict) and isinstance(payload.get("nodes"), list):
            records = payload["nodes"]
        elif isinstance(payload, dict) and all(
            isinstance(payload.get(section), list)
            for section in ("macroareas", "areas", "subareas")
        ):
            records = []
            for section, node_type in (
                ("macroareas", "macroarea"),
                ("areas", "area"),
                ("subareas", "sottoarea"),
            ):
                records.extend({**record, "type": node_type} for record in payload[section])
        else:
            raise ImportParseError("JSON must contain a node list or canonical ontology sections")

        if not all(isinstance(record, dict) for record in records):
            raise ImportParseError("Every imported node must be a JSON object")
        return ParsedOntology("json", self.name, tuple(_source_node(record) for record in records))


def _yaml_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value.casefold() in {"true", "false"}:
        return value.casefold() == "true"
    if value.startswith(('"', "'", "[", "{")):
        try:
            if value.startswith("'") and value.endswith("'"):
                return value[1:-1].replace("''", "'")
            return json.loads(value)
        except json.JSONDecodeError:
            return value.strip("\"'")
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return value


class YamlOntologyParser:
    """Parse deterministic, flat ontology records from a YAML sequence."""

    name = "yaml-internal"

    def accepts(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith((".yaml", ".yml"))

    def parse(self, content: bytes) -> ParsedOntology:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ImportParseError("YAML file is not UTF-8") from exc
        records: list[dict[str, Any]] = []
        current: dict[str, Any] | None = None
        section_type: str | None = None
        section_types = {
            "macroareas": "macroarea",
            "areas": "area",
            "subareas": "sottoarea",
            "nodes": None,
        }
        for line_number, raw_line in enumerate(text.splitlines(), 1):
            line = raw_line.split(" #", 1)[0].rstrip()
            if not line.strip() or line.lstrip().startswith("#") or line.strip() == "---":
                continue
            stripped = line.strip()
            if not line.startswith((" ", "\t")) and stripped.endswith(":"):
                section = stripped[:-1]
                if section not in section_types:
                    raise ImportParseError(f"Unsupported YAML section {section!r}")
                section_type = section_types[section]
                continue
            if stripped.startswith("-"):
                if current is not None:
                    records.append(current)
                current = {}
                if section_type:
                    current["type"] = section_type
                remainder = stripped[1:].strip()
                if remainder:
                    self._field(current, remainder, line_number)
                continue
            if current is None:
                raise ImportParseError(f"Expected a YAML node at line {line_number}")
            self._field(current, stripped, line_number)
        if current is not None:
            records.append(current)
        if not records:
            raise ImportParseError("No YAML ontology records found")
        return ParsedOntology("yaml", self.name, tuple(_source_node(record) for record in records))

    @staticmethod
    def _field(record: dict[str, Any], line: str, line_number: int) -> None:
        if ":" not in line:
            raise ImportParseError(f"Invalid YAML field at line {line_number}")
        key, value = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            raise ImportParseError(f"Invalid YAML key at line {line_number}")
        record[key] = _yaml_scalar(value)


class MarkdownOntologyParser:
    name = "markdown-internal"

    def accepts(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".md")

    def parse(self, content: bytes) -> ParsedOntology:
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ImportParseError("Markdown file is not UTF-8") from exc
        fence = re.search(r"```(json|yaml|yml)\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE)
        if fence:
            parser: OntologyParser = (
                JsonOntologyParser()
                if fence.group(1).casefold() == "json"
                else YamlOntologyParser()
            )
            parsed = parser.parse(fence.group(2).encode("utf-8"))
            return ParsedOntology("markdown", self.name, parsed.nodes)
        records = self._table(text)
        if not records:
            raise ImportParseError("Markdown must contain a JSON/YAML fence or ontology table")
        return ParsedOntology(
            "markdown", self.name, tuple(_source_node(record) for record in records)
        )

    @staticmethod
    def _table(text: str) -> list[dict[str, Any]]:
        lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
        if len(lines) < 3:
            return []
        rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
        headers = [header.casefold() for header in rows[0]]
        if not {"id", "type", "label", "description"}.issubset(headers):
            return []
        if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in rows[1]):
            return []
        return [
            {header: _yaml_scalar(value) for header, value in zip(headers, row, strict=False)}
            for row in rows[2:]
        ]


class DocxOntologyParser:
    name = "docx-internal"
    _namespace: ClassVar[dict[str, str]] = {
        "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    }

    def accepts(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".docx")

    def parse(self, content: bytes) -> ParsedOntology:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                document = archive.read("word/document.xml")
        except (zipfile.BadZipFile, KeyError) as exc:
            raise ImportParseError("Invalid DOCX document") from exc
        try:
            root = ElementTree.fromstring(document)
        except ElementTree.ParseError as exc:
            raise ImportParseError("Malformed DOCX XML") from exc
        tables = root.findall(".//w:tbl", self._namespace)
        document_records: list[dict[str, Any]] = []
        for table in tables:
            rows = []
            for row in table.findall("./w:tr", self._namespace):
                cells = [
                    "".join(cell.itertext()).strip()
                    for cell in row.findall("./w:tc", self._namespace)
                ]
                rows.append(cells)
            records = self._records(rows)
            if records:
                document_records.extend(records)
        if document_records:
            return ParsedOntology(
                "docx",
                self.name,
                tuple(_source_node(record) for record in document_records),
            )
        paragraphs = [
            "".join(paragraph.itertext()) for paragraph in root.findall(".//w:p", self._namespace)
        ]
        parsed = MarkdownOntologyParser().parse("\n".join(paragraphs).encode("utf-8"))
        return ParsedOntology("docx", self.name, parsed.nodes)

    @staticmethod
    def _records(rows: list[list[str]]) -> list[dict[str, Any]]:
        if len(rows) < 2:
            return []
        headers = [header.casefold() for header in rows[0]]
        if not {"id", "type", "label", "description"}.issubset(headers):
            return []
        return [
            {header: _yaml_scalar(value) for header, value in zip(headers, row, strict=False)}
            for row in rows[1:]
            if row and row[0].strip()
        ]


def _literal(node: ast.AST, context: str) -> Any:
    try:
        return ast.literal_eval(node)
    except (ValueError, TypeError) as exc:
        raise ImportParseError(f"{context} must contain literal values only") from exc


class KimiPythonParser:
    """Read Kimi add_node/ONTO files through AST without executing them."""

    name = "kimi-python"

    def accepts(self, filename: str, content: bytes) -> bool:
        return filename.lower().endswith(".py") or b"add_node(" in content or b"ONTO" in content

    @staticmethod
    def _add_node(call: ast.Call) -> SourceNode:
        values = {
            name: _literal(value, "add_node")
            for name, value in zip(KIMI_ARGUMENTS, call.args, strict=False)
        }
        values.update(
            {
                keyword.arg: _literal(keyword.value, "add_node")
                for keyword in call.keywords
                if keyword.arg is not None
            }
        )
        return _source_node(values)

    def parse(self, content: bytes) -> ParsedOntology:
        try:
            module = ast.parse(content.decode("utf-8-sig"))
        except UnicodeDecodeError as exc:
            raise ImportParseError("Python file is not UTF-8") from exc
        except SyntaxError as exc:
            raise ImportParseError(f"Invalid Python syntax at line {exc.lineno}") from exc

        reset_lines = [
            statement.lineno
            for statement in module.body
            if isinstance(statement, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "nodes"
                for target in statement.targets
            )
            and isinstance(statement.value, ast.Dict)
            and not statement.value.keys
        ]
        start_line = max(reset_lines, default=0)
        nodes: list[SourceNode] = []
        structures: dict[str, dict[str, Any]] = {}
        expand_calls: list[tuple[Any, dict[str, Any]]] = []
        for statement in module.body:
            if statement.lineno < start_line:
                continue
            if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                call = statement.value
                if isinstance(call.func, ast.Name) and call.func.id == "add_node":
                    nodes.append(self._add_node(call))
                elif (
                    isinstance(call.func, ast.Name)
                    and call.func.id == "expand"
                    and len(call.args) >= 2
                ):
                    if isinstance(call.args[1], ast.Name):
                        structure = structures.get(call.args[1].id)
                        if structure is None:
                            raise ImportParseError(f"Unknown expand structure: {call.args[1].id}")
                    else:
                        structure = _literal(call.args[1], "expand structure")
                        if not isinstance(structure, dict):
                            raise ImportParseError("expand structure must be an object")
                    expand_calls.append((_literal(call.args[0], "expand parent"), structure))
            elif isinstance(statement, (ast.Assign, ast.AnnAssign)):
                target = (
                    statement.targets[0] if isinstance(statement, ast.Assign) else statement.target
                )
                value = statement.value
                if isinstance(target, ast.Name) and value is not None:
                    try:
                        literal = ast.literal_eval(value)
                    except (ValueError, TypeError):
                        continue
                    if isinstance(literal, dict):
                        structures[target.id] = literal

        for parent, structure in expand_calls:
            self._expand(nodes, parent, structure)
        if not nodes:
            raise ImportParseError("No add_node or expand ontology records found")
        return ParsedOntology("python", self.name, tuple(nodes))

    def _expand(
        self,
        nodes: list[SourceNode],
        parent: str | None,
        structure: dict[str, Any],
    ) -> None:
        for suffix, data in structure.items():
            if not isinstance(suffix, str) or not isinstance(data, dict):
                raise ImportParseError("ONTO structures must map string IDs to objects")
            identifier = f"{parent}.{suffix}" if parent else suffix
            record = {
                "id": identifier,
                "label": data.get("label"),
                "description": data.get("desc", data.get("label")),
                "parent": parent,
                "type": data.get("type", "categoria"),
                "language": data.get("language", "it"),
            }
            record.update({key: value for key, value in data.items() if key != "children"})
            nodes.append(_source_node(record))
            children = data.get("children")
            if children is not None:
                if not isinstance(children, dict):
                    raise ImportParseError(f"{identifier} children must be an object")
                self._expand(nodes, identifier, children)


class ParserRegistry:
    def __init__(self, parsers: tuple[OntologyParser, ...] | None = None) -> None:
        self.parsers = parsers or (
            JsonOntologyParser(),
            YamlOntologyParser(),
            MarkdownOntologyParser(),
            DocxOntologyParser(),
            KimiPythonParser(),
        )

    def parse(self, filename: str, content: bytes | str) -> ParsedOntology:
        raw_content = content.encode("utf-8") if isinstance(content, str) else content
        errors: list[str] = []
        for parser in self.parsers:
            if not parser.accepts(filename, raw_content):
                continue
            try:
                return parser.parse(raw_content)
            except ImportParseError as exc:
                errors.append(f"{parser.name}: {exc}")
        if errors:
            raise ImportParseError("; ".join(errors))
        raise ImportParseError("Unrecognized ontology format")
