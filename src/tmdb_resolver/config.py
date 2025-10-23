import logging
from dataclasses import dataclass
from typing import Self

import sentry_sdk
from bs_config import Env

_logger = logging.getLogger(__name__)


@dataclass
class TmdbConfig:
    api_token: str

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            api_token=env.get_string("api-token", required=True),
        )


@dataclass
class Config:
    app_version: str
    sentry_dsn: str | None
    tmdb: TmdbConfig

    @classmethod
    def from_env(cls, env: Env) -> Self:
        return cls(
            app_version=env.get_string("app-version", default="dev"),
            sentry_dsn=env.get_string("sentry-dsn"),
            tmdb=TmdbConfig.from_env(env / "tmdb"),
        )


def _set_up_logging(config: Config) -> None:
    logging.basicConfig()
    logging.getLogger(__package__).setLevel(logging.DEBUG)
    dsn = config.sentry_dsn
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            release=config.app_version,
        )
    else:
        _logger.warning("Sentry is disabled")


def load_config() -> Config:
    env = Env.load(include_default_dotenv=True)
    config = Config.from_env(env)
    _set_up_logging(config)
    return config
