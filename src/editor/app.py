"""FastAPI application for offline ontology editing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from scripts.generate_seed import ONTOLOGY_DIR

from .contribution import ContributionError, ContributionService
from .importer import ImportManager
from .models import ContributionActionInput, ImportConfirmInput, NodeInput
from .quality import KnowledgeQualityCenter
from .store import EditorError, OntologyStore

STATIC_DIR = Path(__file__).with_name("static")


def _validation_payload(valid: bool, errors: tuple[str, ...]) -> dict[str, Any]:
    return {"valid": valid, "errors": list(errors)}


def create_app(ontology_dir: Path = ONTOLOGY_DIR) -> FastAPI:
    """Create an editor application for a canonical ontology directory."""
    app = FastAPI(title="Italian Knowledge Graph Ontology Editor")
    store = OntologyStore(ontology_dir)
    import_manager = ImportManager(ontology_dir / "import_mappings.json")
    quality_center = KnowledgeQualityCenter()
    contribution_service = ContributionService(store, quality_center, ontology_dir.parent)
    app.state.store = store
    app.state.import_manager = import_manager
    app.state.quality_center = quality_center
    app.state.contribution_service = contribution_service

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/tree")
    def tree(q: str = Query(default="")) -> list[dict[str, Any]]:
        return store.tree(q)

    @app.get("/api/suggest-id")
    def suggest_id(label: str, parent_id: str | None = None) -> dict[str, Any]:
        try:
            return store.suggest_id(parent_id, label)
        except EditorError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.get("/api/node/{node_id}")
    def get_node(node_id: str) -> dict[str, Any]:
        try:
            return store.node(node_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown node: {node_id}") from exc

    @app.put("/api/node/{node_id}")
    def update_node(node_id: str, payload: NodeInput) -> dict[str, Any]:
        try:
            return store.update(node_id, payload.model_dump())
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown node: {node_id}") from exc
        except EditorError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/api/node", status_code=201)
    def create_node(payload: NodeInput) -> dict[str, Any]:
        try:
            return store.create(payload.model_dump())
        except EditorError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.delete("/api/node/{node_id}", status_code=204)
    def delete_node(node_id: str) -> None:
        try:
            store.delete(node_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=f"Unknown node: {node_id}") from exc
        except EditorError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/api/validate")
    def validate() -> dict[str, Any]:
        result = store.validate()
        return _validation_payload(result.valid, result.errors)

    @app.post("/api/save")
    def save() -> JSONResponse:
        result = store.save()
        payload = _validation_payload(result.valid, result.errors)
        payload["saved"] = result.valid
        return JSONResponse(payload, status_code=200 if result.valid else 422)

    @app.post("/api/discard")
    def discard() -> dict[str, bool]:
        store.reload()
        return {"discarded": True}

    @app.post("/api/import/preview")
    async def import_preview(
        request: Request,
        filename: str = Query(min_length=1),
        mode: str = Query(default="assisted"),
        mappings: str = Query(default="{}"),
        persist_mappings: bool = Query(default=False),
    ) -> dict[str, object]:
        content = bytearray()
        async for chunk in request.stream():
            content.extend(chunk)
        if not content:
            raise HTTPException(status_code=422, detail="Import file is empty")
        try:
            mapping_payload = json.loads(mappings)
        except json.JSONDecodeError as exc:
            raise HTTPException(status_code=422, detail="Mappings must be valid JSON") from exc
        if not isinstance(mapping_payload, dict) or not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in mapping_payload.items()
        ):
            raise HTTPException(status_code=422, detail="Mappings must be a string map")
        return import_manager.preview(
            store,
            filename,
            bytes(content),
            mode,
            mapping_payload,
            persist_mappings,
        ).as_dict()

    @app.post("/api/import/confirm")
    def import_confirm(payload: ImportConfirmInput) -> dict[str, object]:
        try:
            report = import_manager.confirm(
                store,
                payload.token,
                payload.accepted_warnings,
            )
        except KeyError as exc:
            raise HTTPException(
                status_code=404, detail="Unknown or expired import preview"
            ) from exc
        except EditorError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        return {"imported": True, "report": report.as_dict()}

    @app.get("/api/quality/report")
    def quality_report() -> dict[str, object]:
        return quality_center.evaluate(store.snapshot(), store.activity()).as_dict()

    @app.get("/api/contribution/status")
    def contribution_status() -> dict[str, bool]:
        return {"changed": contribution_service.changes().changed}

    @app.get("/api/contribution/preview")
    def contribution_preview() -> dict[str, object]:
        return contribution_service.preview().as_dict()

    @app.post("/api/contribution/package")
    def contribution_package(payload: ContributionActionInput) -> dict[str, object]:
        try:
            return contribution_service.export_package(
                payload.filename or "ikg-contribution.zip",
                payload.accepted_warning_ids,
            )
        except ContributionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    @app.post("/api/contribution/git")
    def contribution_git(payload: ContributionActionInput) -> dict[str, object]:
        try:
            return contribution_service.prepare_git(payload.accepted_warning_ids)
        except ContributionError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc

    return app
