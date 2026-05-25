from datetime import datetime

from pydantic import BaseModel, Field

from app.models.project import ProjectStatus
from app.schemas.place import PlaceCreate, PlaceResponse


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    start_date: datetime | None = None
    places: list[PlaceCreate] = Field(default_factory=list, max_length=10)


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    start_date: datetime | None = None


class ProjectResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    description: str | None
    start_date: datetime | None
    status: ProjectStatus
    created_at: datetime
    places: list[PlaceResponse] = []
