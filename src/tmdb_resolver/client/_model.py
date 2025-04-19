import abc
import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, HttpUrl

from tmdb_resolver import model
from tmdb_resolver.model import CoverMetadata


class TmdbResponse(BaseModel, abc.ABC):
    model_config = ConfigDict(
        frozen=True,
    )


class ApiImagesConfiguration(TmdbResponse):
    base_url: HttpUrl
    secure_base_url: HttpUrl
    logo_sizes: list[str]
    poster_sizes: list[str]

    def select_poster_size(self, *, original: int, target: int) -> str:
        pattern = re.compile(r"\d+")
        nums = []

        available = self.poster_sizes
        for size in available:
            if size == "original":
                nums.append(original)
            elif match := pattern.search(size):
                nums.append(int(match.group(0)))
            else:
                raise ValueError(f"Could not parse size {size}")

        selected_width = min(nums, key=lambda n: abs(n - target))
        return available[nums.index(selected_width)]


class ApiConfiguration(TmdbResponse):
    images: ApiImagesConfiguration
    change_keys: list[str]


class Genre(TmdbResponse):
    id: int
    name: str


class Movie(TmdbResponse):
    adult: bool
    id: int
    original_language: str
    release_date: datetime
    poster_path: str | None
    title: str
    vote_count: int
    vote_average: float
    imdb_id: str | None = None

    def to_model(self, cover: model.CoverMetadata | None) -> model.Movie:
        return model.Movie(
            id=str(self.id),
            title=self.title,
            year=self.release_date.year,
            cover=cover,
            rating=f"{self.vote_average:.1f}",
        )


class MovieResults(TmdbResponse):
    movie_results: list[Movie]


class Image(TmdbResponse):
    aspect_ratio: float
    height: int
    width: int
    vote_count: int
    vote_average: float
    file_path: str

    def to_model(
        self, images_config: ApiImagesConfiguration, target_width: int = 200
    ) -> CoverMetadata:
        base_url = str(images_config.secure_base_url)
        width = images_config.select_poster_size(
            original=self.width, target=target_width
        )
        image_url = f"{base_url}{width}{self.file_path}"

        return CoverMetadata(
            ratio=self.aspect_ratio,
            url=str(image_url),  # type: ignore
        )


class MovieImages(TmdbResponse):
    id: int
    posters: list[Image]
