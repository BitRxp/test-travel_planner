from sqlalchemy.orm import Session

from app.artic import client as artic_client
from app.core.exceptions import ProjectHasVisitedPlaces, ProjectNotFound
from app.crud import places as places_crud
from app.crud import projects as projects_crud
from app.models.project import ProjectStatus, TravelProject
from app.schemas.project import ProjectCreate, ProjectUpdate


async def create_project(db: Session, data: ProjectCreate) -> TravelProject:
    project = projects_crud.create(
        db,
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )

    for place_data in data.places:
        artwork = await artic_client.get_artwork(place_data.external_id)
        places_crud.create(
            db,
            project_id=project.id,
            external_id=artwork.id,
            title=artwork.title,
            image_url=artwork.image_url,
        )

    db.refresh(project)
    return project


def get_project(db: Session, project_id: int) -> TravelProject:
    project = projects_crud.get_by_id(db, project_id)
    if not project:
        raise ProjectNotFound()
    return project


def get_projects(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: ProjectStatus | None = None,
) -> list[TravelProject]:
    return projects_crud.get_list(db, skip=skip, limit=limit, status=status)


def update_project(db: Session, project_id: int, data: ProjectUpdate) -> TravelProject:
    project = get_project(db, project_id)
    return projects_crud.update(
        db,
        project,
        name=data.name,
        description=data.description,
        start_date=data.start_date,
    )


def delete_project(db: Session, project_id: int) -> None:
    project = get_project(db, project_id)

    has_visited = any(place.visited for place in project.places)
    if has_visited:
        raise ProjectHasVisitedPlaces()

    projects_crud.delete(db, project)


def sync_project_status(db: Session, project: TravelProject) -> None:
    places = project.places
    if places and all(place.visited for place in places):
        projects_crud.update(db, project, status=ProjectStatus.completed)
