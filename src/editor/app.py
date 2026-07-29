"""FastAPI application for offline ontology editing."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from scripts.generate_seed import ONTOLOGY_DIR

from .models import NodeInput
from .store import EditorError, OntologyStore

STATIC_DIR = Path(__file__).with_name("static")


def _validation_payload(valid: bool, errors: tuple[str, ...]) -> dict[str, Any]:
    return {"valid": valid, "errors": list(errors)}


def create_app(ontology_dir: Path = ONTOLOGY_DIR) -> FastAPI:
    """Create an editor application for a canonical ontology directory."""
    app = FastAPI(title="Italian Knowledge Graph Ontology Editor")
    store = OntologyStore(ontology_dir)
    app.state.store = store

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

    return app
