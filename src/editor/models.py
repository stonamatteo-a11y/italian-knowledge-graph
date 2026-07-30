"""API models for ontology editing."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class NodeInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    type: str = Field(min_length=1)
    label: str = Field(min_length=1)
    description: str = Field(min_length=1)
    parent_id: str | None = None
    language: str = Field(default="it", min_length=1)


class ImportConfirmInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    token: str = Field(min_length=1)
    accepted_warnings: tuple[str, ...] = ()
    mode: Literal["assisted", "automatic"] = "assisted"


class ContributionActionInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    accepted_warning_ids: tuple[str, ...] = ()
    filename: str | None = None
