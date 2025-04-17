from typing import Any, TypedDict

import httpx
import pytest

from tmdb_resolver.model import CoverMetadata

IGNORE_FIELDS = {"cover", "rating"}
EXAMPLE_URL_HOLIDATE = "https://www.themoviedb.org/movie/615665-holidate"
EXAMPLE_DATA_HOLIDATE = {
    "id": "615665",
    "title": "Holidate",
    "year": 2020,
}


class ExpectedResponse(TypedDict):
    code: int
    data: dict[str, Any]


def assert_response_payload(*, expected: dict, actual: dict) -> None:
    for field in IGNORE_FIELDS:
        assert actual.get(field)
        del actual[field]

    assert actual == expected


@pytest.mark.parametrize(
    "url",
    [
        EXAMPLE_URL_HOLIDATE,
        "https://www.imdb.com/title/tt9866072/",
    ],
)
def test_by_link(client, url):
    response = client.post(
        "/by_link",
        json={"link": url},
    )

    assert response.status_code == 200
    assert_response_payload(
        expected=EXAMPLE_DATA_HOLIDATE,
        actual=response.json(),
    )


def test_get_cover(client):
    response = client.post("/by_link", json={"link": EXAMPLE_URL_HOLIDATE})
    response.raise_for_status()

    cover_data = response.json()["cover"]
    cover = CoverMetadata.model_validate(cover_data)

    assert cover.url.scheme == "https"

    image_response = httpx.head(str(cover.url))
    assert image_response.status_code == 200
    assert image_response.headers["content-type"] == "image/jpeg"
    assert int(image_response.headers["content-length"]) > 0
