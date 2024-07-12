from collections.abc import AsyncIterator, Iterator
from typing import Any, Self
from unittest.mock import patch

from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from fastapi_lifespan_dependencies import Lifespan


class SyncResource:
    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_: Any) -> None:
        pass


class AsyncResource:
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_: Any) -> None:
        pass


lifespan = Lifespan()


@lifespan.register
def sync_dependency() -> Iterator[SyncResource]:
    with SyncResource() as resource:
        yield resource


@lifespan.register
async def async_dependency() -> AsyncIterator[AsyncResource]:
    async with AsyncResource() as resource:
        yield resource


app = FastAPI(lifespan=lifespan)


async def test_sync_resource_management() -> None:
    with (
        patch.object(SyncResource, "__enter__") as enter_mock,
        patch.object(SyncResource, "__exit__") as exit_mock,
    ):
        async with LifespanManager(app):
            enter_mock.assert_called_once()
            exit_mock.assert_not_called()

        exit_mock.assert_called_once()


async def test_async_resource_management() -> None:
    with (
        patch.object(AsyncResource, "__aenter__") as enter_mock,
        patch.object(AsyncResource, "__aexit__") as exit_mock,
    ):
        async with LifespanManager(app):
            enter_mock.assert_awaited_once()
            exit_mock.assert_not_called()

        exit_mock.assert_awaited_once()
