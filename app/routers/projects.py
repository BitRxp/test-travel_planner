from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import projects as projects_service

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    return await projects_service.create_project(db, data)


@router.get("", response_model=list[ProjectResponse])
def list_projects(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return projects_service.get_projects(db, skip=skip, limit=limit)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return projects_service.get_project(db, project_id)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    return projects_service.update_project(db, project_id, data)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    projects_service.delete_project(db, project_id)
