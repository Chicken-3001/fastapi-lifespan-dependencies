from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from fastapi_lifespan_dependencies import Lifespan


lifespan = Lifespan()


async def dependency() -> AsyncIterator[int]:
    yield 0


@lifespan.register
async def lifespan_dependency() -> AsyncIterator[int]:
    yield 1


@lifespan.register
async def sync_lifespan_dependency() -> AsyncIterator[int]:
    yield 2


@lifespan.register
async def dependent(
    value: Annotated[int, Depends(dependency)],
) -> AsyncIterator[int]:
    yield value


@lifespan.register
async def lifespan_dependent(
    value: Annotated[int, Depends(lifespan_dependency)],
) -> AsyncIterator[int]:
    yield value


# TODO: Test async/sync dependency chains?
