from typing import Annotated, AsyncIterator
from asgi_lifespan import LifespanManager
from fastapi import Depends, FastAPI, WebSocket

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


@app.websocket("/lifespan_dependency")
async def get_lifespan_dependency(
    websocket: WebSocket,
    value: Annotated[int, Depends(lifespan_dependency)],
) -> None:
    await websocket.accept()
    await websocket.send_json(value)


@app.websocket("/sync_lifespan_dependency")
async def get_sync_lifespan_dependency(
    websocket: WebSocket,
    value: Annotated[int, Depends(sync_lifespan_dependency)],
) -> None:
    await websocket.accept()
    await websocket.send_json(value)


@app.websocket("/dependent")
async def get_dependent(
    websocket: WebSocket, value: Annotated[int, Depends(dependent)]
) -> None:
    await websocket.accept()
    await websocket.send_json(value)


@app.websocket("/lifespan_dependent")
async def get_lifespan_dependent(
    websocket: WebSocket,
    value: Annotated[int, Depends(lifespan_dependent)],
) -> None:
    await websocket.accept()
    await websocket.send_json(value)


@pytest.fixture
async def client() -> AsyncIterator[TestClient]:
    async with LifespanManager(app) as manager:
        yield TestClient(manager.app)


async def test_lifespan_dependency(client: TestClient) -> None:
    with client.websocket_connect("/lifespan_dependency") as websocket:
        assert websocket.receive_json() == 1


async def test_sync_lifespan_dependency(client: TestClient) -> None:
    with client.websocket_connect("/sync_lifespan_dependency") as websocket:
        assert websocket.receive_json() == 2


async def test_dependent(client: TestClient) -> None:
    with client.websocket_connect("/dependent") as websocket:
        assert websocket.receive_json() == 0


async def test_lifespan_dependent(client: TestClient) -> None:
    with client.websocket_connect("/lifespan_dependent") as websocket:
        assert websocket.receive_json() == 1
