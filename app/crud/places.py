from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.place import ProjectPlace


def create(
    db: Session,
    project_id: int,
    external_id: int,
    title: str,
    image_url: str | None,
) -> ProjectPlace:
    place = ProjectPlace(
        project_id=project_id,
        external_id=external_id,
        title=title,
        image_url=image_url,
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


def get_by_id(db: Session, place_id: int, project_id: int) -> ProjectPlace | None:
    stmt = select(ProjectPlace).where(
        ProjectPlace.id == place_id,
        ProjectPlace.project_id == project_id,
    )
    return db.scalars(stmt).first()


def get_list(
    db: Session,
    project_id: int,
    skip: int = 0,
    limit: int = 20,
    visited: bool | None = None,
) -> list[ProjectPlace]:
    stmt = select(ProjectPlace).where(ProjectPlace.project_id == project_id)
    if visited is not None:
        stmt = stmt.where(ProjectPlace.visited == visited)
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def update(
    db: Session,
    place: ProjectPlace,
    notes: str | None = None,
    visited: bool | None = None,
) -> ProjectPlace:
    if notes is not None:
        place.notes = notes
    if visited is not None:
        place.visited = visited
    db.commit()
    db.refresh(place)
    return place


def count_by_project(db: Session, project_id: int) -> int:
    stmt = select(func.count()).where(ProjectPlace.project_id == project_id)
    return db.scalar(stmt) or 0


def check_duplicate(db: Session, project_id: int, external_id: int) -> bool:
    stmt = select(ProjectPlace.id).where(
        ProjectPlace.project_id == project_id,
        ProjectPlace.external_id == external_id,
    )
    return db.scalars(stmt).first() is not None
