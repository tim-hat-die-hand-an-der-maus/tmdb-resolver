from typing import Self

from pydantic import BaseModel

from tmdb_resolver.client._model import ApiConfiguration


class State(BaseModel):
    api_config: ApiConfiguration | None

    @classmethod
    def initial(cls) -> Self:
        return cls(
            api_config=None,
        )
