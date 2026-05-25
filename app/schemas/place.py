from datetime import datetime

from pydantic import BaseModel, Field


class PlaceCreate(BaseModel):
    external_id: int


class PlaceUpdate(BaseModel):
    notes: str | None = Field(default=None, max_length=5000)
    visited: bool | None = None


class PlaceResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    project_id: int
    external_id: int
    title: str
    image_url: str | None
    notes: str | None
    visited: bool
    created_at: datetime
