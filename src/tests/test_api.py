IGNORE_FIELDS = {"cover", "coverUrl", "rating"}


def get_test_data():
    return {
        "https://www.themoviedb.org/movie/615665-holidate": {
            "code": 200,
            "data": {
                "id": "615665",
                "title": "Holidate",
                "year": 2020,
            },
        }
    }


def compare_results_by_url(imdb_id: str, actual: dict) -> bool:
    expected: dict = get_test_data()[imdb_id]["data"]
    comparable_keys = expected.keys() - IGNORE_FIELDS

    result = {}
    for key in comparable_keys:
        result[key] = expected[key] == actual[key]

    return all(e[1] for e in result.items())


def test_url(client):
    for url in get_test_data().keys():
        response = client.post(
            "/by_link",
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json={"tmdbUrl": url},
        )

        assert response.status_code == get_test_data()[url].get("code", 200)
        assert compare_results_by_url(url, response.json())
