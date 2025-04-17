from typing import Protocol

from bs_state.implementation import memory_storage
from bs_state.storage import StateStorage
from pydantic import BaseModel


class StateStorageLoader(Protocol):
    async def __call__[T: BaseModel](self, initial_state: T) -> StateStorage[T]:
        pass


async def __init_memory_storage[T: BaseModel](initial_state: T) -> StateStorage[T]:
    return await memory_storage.load(initial_state=initial_state)


async def init_state_storage_loader() -> StateStorageLoader:
    return __init_memory_storage
