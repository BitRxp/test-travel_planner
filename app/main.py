from fastapi import FastAPI

from app.config import settings

app = FastAPI(
    title="Travel Planner",
    description="API for managing travel projects and places",
    version="1.0.0",
)

# Routers will be registered here as they are implemented
# from app.routers import projects, places
# app.include_router(projects.router, prefix=settings.API_PREFIX)
# app.include_router(places.router, prefix=settings.API_PREFIX)

# Exception handlers will be registered here
# from app.core.exceptions import register_exception_handlers
# register_exception_handlers(app)


@app.get("/health")
def health_check():
    return {"status": "ok"}
