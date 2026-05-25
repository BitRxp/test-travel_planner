from pydantic import BaseModel, model_validator


class ArtworkData(BaseModel):
    id: int
    title: str
    image_id: str | None = None

    # resolved from config.iiif_url + image_id — set by client after parsing
    image_url: str | None = None


class ArticConfig(BaseModel):
    iiif_url: str


class ArticPagination(BaseModel):
    total: int
    limit: int
    offset: int
    total_pages: int
    current_page: int


class ArtworkDetailResponse(BaseModel):
    data: ArtworkData
    config: ArticConfig

    @model_validator(mode="after")
    def resolve_image_url(self) -> "ArtworkDetailResponse":
        if self.data.image_id:
            self.data.image_url = (
                f"{self.config.iiif_url}/{self.data.image_id}/full/843,/0/default.jpg"
            )
        return self


class ArtworkSearchResponse(BaseModel):
    data: list[ArtworkData]
    config: ArticConfig
    pagination: ArticPagination

    @model_validator(mode="after")
    def resolve_image_urls(self) -> "ArtworkSearchResponse":
        for artwork in self.data:
            if artwork.image_id:
                artwork.image_url = (
                    f"{self.config.iiif_url}/{artwork.image_id}/full/843,/0/default.jpg"
                )
        return self
