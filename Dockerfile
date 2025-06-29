FROM ghcr.io/astral-sh/uv:0.7.15-python3.13-bookworm-slim

RUN apt-get update -qq \
    && apt-get install -yq --no-install-recommends tini  \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /var/cache/apt/archives/*

RUN groupadd --system --gid 1000 app \
    && useradd --system --uid 1000 --gid app --create-home --home-dir /app app

USER 1000
WORKDIR /app

COPY [ "uv.lock", "pyproject.toml", "./" ]

RUN uv sync --locked --no-install-workspace --all-extras --no-dev

# We don't want the tests
COPY src/tmdb_resolver ./src/tmdb_resolver

RUN uv sync --locked --no-editable --all-extras --no-dev

ARG APP_VERSION
ENV APP_VERSION=$APP_VERSION

EXPOSE 8000

ENV TZ=Etc/UTC
ENV UV_NO_SYNC=true
ENTRYPOINT ["tini", "--", "uv", "run"]
CMD ["uvicorn", "tmdb_resolver.api:app", "--host=0.0.0.0"]
