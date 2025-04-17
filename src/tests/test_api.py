from typing import Any, TypedDict

import pytest

IGNORE_FIELDS = {"cover", "rating"}
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
        assert field in actual
        del actual[field]

    assert actual == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://www.themoviedb.org/movie/615665-holidate",
        "https://www.imdb.com/title/tt9866072/",
    ],
)
def test_by_link(client, url):
    response = client.post(
        "/by_link",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json={"link": url},
    )

    assert response.status_code == 200
    assert_response_payload(
        expected=EXAMPLE_DATA_HOLIDATE,
        actual=response.json(),
    )
