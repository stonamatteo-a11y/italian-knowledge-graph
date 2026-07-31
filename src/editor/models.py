"""API models for ontology editing."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class SourceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    url: str | None = None
    title: str | None = None
    publisher: str | None = None
    accessed_at: str | None = None
    note: str | None = None


class RelationInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    predicate: str = Field(min_length=1)
    target_id: str = Field(min_length=1)
    note: str | None = None


class NodeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    label: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parent_id: str | None = None
    language: str = Field(default="it", min_length=1)
    aliases: tuple[str, ...] = ()
    sources: tuple[SourceInput, ...] = ()
    notes: tuple[str, ...] = ()
    relations: tuple[RelationInput, ...] = ()


class ImportConfirmInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    accepted_warnings: tuple[str, ...] = ()
    mode: Literal["assisted", "automatic"] = "assisted"


class ContributionActionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accepted_warning_ids: tuple[str, ...] = ()
    filename: str | None = None


class GuidedContributionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    domain_id: str = Field(min_length=1)
    area_id: str | None = None
    subarea_id: str | None = None
    node_id: str | None = None
    fields: tuple[str, ...] = ()
    node_limit: Literal["selected", "10", "25", "50", "all"] = "10"
    filename: str = "ikg-guided-contribution.zip"
