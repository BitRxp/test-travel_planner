from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.schemas.place import PlaceCreate, PlaceResponse, PlaceUpdate
from app.services import places as places_service

router = APIRouter(
    prefix="/projects/{project_id}/places",
    tags=["Places"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=PlaceResponse, status_code=status.HTTP_201_CREATED)
async def add_place(project_id: int, data: PlaceCreate, db: Session = Depends(get_db)):
    return await places_service.add_place(db, project_id, data)


@router.get("", response_model=list[PlaceResponse])
def list_places(
    project_id: int,
    skip: int = 0,
    limit: int = 20,
    visited: bool | None = None,
    db: Session = Depends(get_db),
):
    return places_service.get_places(db, project_id, skip=skip, limit=limit, visited=visited)


@router.get("/{place_id}", response_model=PlaceResponse)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    return places_service.get_place(db, project_id, place_id)


@router.patch("/{place_id}", response_model=PlaceResponse)
def update_place(
    project_id: int,
    place_id: int,
    data: PlaceUpdate,
    db: Session = Depends(get_db),
):
    return places_service.update_place(db, project_id, place_id, data)
