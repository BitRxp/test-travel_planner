from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


# --- Base ---

class AppError(Exception):
    status_code: int = 500
    detail: str = "Internal server error"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


# --- Project ---

class ProjectNotFound(AppError):
    status_code = 404
    detail = "Project not found"


class ProjectHasVisitedPlaces(AppError):
    status_code = 409
    detail = "Cannot delete project: it has visited places"


# --- Place ---

class PlaceNotFound(AppError):
    status_code = 404
    detail = "Place not found"


class PlaceLimitExceeded(AppError):
    status_code = 422
    detail = "Project cannot have more than 10 places"


class DuplicatePlace(AppError):
    status_code = 409
    detail = "This place is already added to the project"


# --- Artic API ---

class ArtworkNotFound(AppError):
    status_code = 404
    detail = "Artwork not found in Art Institute of Chicago API"


class ArticAPIError(AppError):
    status_code = 502
    detail = "Art Institute of Chicago API is unavailable"


# --- Handlers ---

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
