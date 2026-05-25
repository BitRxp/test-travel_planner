from fastapi import FastAPI

from app.config import settings
from app.core.exceptions import register_exception_handlers
from app.routers import places, projects

app = FastAPI(
    title="Travel Planner",
    description="API for managing travel projects and places",
    version="1.0.0",
)

register_exception_handlers(app)

app.include_router(projects.router, prefix=settings.API_PREFIX)
app.include_router(places.router, prefix=settings.API_PREFIX)


@app.get("/health")
def health_check():
    return {"status": "ok"}
