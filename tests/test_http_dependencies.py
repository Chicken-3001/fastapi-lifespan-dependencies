from typing import Annotated, AsyncIterator
from asgi_lifespan import LifespanManager
from fastapi import Depends, FastAPI

from fastapi.testclient import TestClient
import pytest

from .dependencies import (
    lifespan,
    lifespan_dependency,
    dependent,
    lifespan_dependent,
    sync_lifespan_dependency,
)


app = FastAPI(lifespan=lifespan)


@app.get("/lifespan_dependency")
async def get_lifespan_dependency(
    value: Annotated[int, Depends(lifespan_dependency)],
) -> int:
    print(value)
    return value


@app.get("/sync_lifespan_dependency")
async def get_sync_lifespan_dependency(
    value: Annotated[int, Depends(sync_lifespan_dependency)],
) -> int:
    return value


@app.get("/dependent")
async def get_dependent(value: Annotated[int, Depends(dependent)]) -> int:
    return value


@app.get("/lifespan_dependent")
async def get_lifespan_dependent(
    value: Annotated[int, Depends(lifespan_dependent)],
) -> int:
    return value


@pytest.fixture
async def client() -> AsyncIterator[TestClient]:
    async with LifespanManager(app) as manager:
        yield TestClient(manager.app)


async def test_lifespan_dependency(client: TestClient) -> None:
    response = client.get("/lifespan_dependency")

    assert response.json() == 1


async def test_sync_lifespan_dependency(client: TestClient) -> None:
    response = client.get("/sync_lifespan_dependency")

    assert response.json() == 2


async def test_dependent(client: TestClient) -> None:
    response = client.get("/dependent")

    assert response.json() == 0


async def test_lifespan_dependent(client: TestClient) -> None:
    response = client.get("/lifespan_dependent")

    assert response.json() == 1
