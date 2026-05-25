from sqlalchemy.orm import Session

from app.artic import client as artic_client
from app.core.exceptions import DuplicatePlace, PlaceLimitExceeded, PlaceNotFound
from app.crud import places as places_crud
from app.models.place import ProjectPlace
from app.schemas.place import PlaceCreate, PlaceUpdate
from app.services import projects as projects_service

MAX_PLACES_PER_PROJECT = 10


async def add_place(db: Session, project_id: int, data: PlaceCreate) -> ProjectPlace:
    project = projects_service.get_project(db, project_id)

    count = places_crud.count_by_project(db, project_id)
    if count >= MAX_PLACES_PER_PROJECT:
        raise PlaceLimitExceeded()

    if places_crud.check_duplicate(db, project_id, data.external_id):
        raise DuplicatePlace()

    artwork = await artic_client.get_artwork(data.external_id)

    place = places_crud.create(
        db,
        project_id=project.id,
        external_id=artwork.id,
        title=artwork.title,
        image_url=artwork.image_url,
    )
    return place


def get_place(db: Session, project_id: int, place_id: int) -> ProjectPlace:
    projects_service.get_project(db, project_id)

    place = places_crud.get_by_id(db, place_id=place_id, project_id=project_id)
    if not place:
        raise PlaceNotFound()
    return place


def get_places(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 20,
    visited: bool | None = None,
) -> list[ProjectPlace]:
    projects_service.get_project(db, project_id)
    return places_crud.get_list(db, project_id=project_id, skip=skip, limit=limit, visited=visited)


def update_place(db: Session, project_id: int, place_id: int, data: PlaceUpdate) -> ProjectPlace:
    place = get_place(db, project_id, place_id)

    place = places_crud.update(db, place, notes=data.notes, visited=data.visited)

    if data.visited is True:
        project = place.project
        projects_service.sync_project_status(db, project)

    return place
