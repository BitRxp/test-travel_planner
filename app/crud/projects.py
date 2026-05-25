from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import ProjectStatus, TravelProject


def create(
    db: Session,
    name: str,
    description: str | None,
    start_date: datetime | None,
) -> TravelProject:
    project = TravelProject(name=name, description=description, start_date=start_date)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_by_id(db: Session, project_id: int) -> TravelProject | None:
    return db.get(TravelProject, project_id)


def get_list(db: Session, skip: int = 0, limit: int = 20) -> list[TravelProject]:
    stmt = select(TravelProject).offset(skip).limit(limit)
    return list(db.scalars(stmt).all())


def update(
    db: Session,
    project: TravelProject,
    name: str | None = None,
    description: str | None = None,
    start_date: datetime | None = None,
    status: ProjectStatus | None = None,
) -> TravelProject:
    if name is not None:
        project.name = name
    if description is not None:
        project.description = description
    if start_date is not None:
        project.start_date = start_date
    if status is not None:
        project.status = status
    db.commit()
    db.refresh(project)
    return project


def delete(db: Session, project: TravelProject) -> None:
    db.delete(project)
    db.commit()
