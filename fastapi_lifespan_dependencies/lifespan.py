from typing import Any, AsyncIterator, Callable, Mapping, TypeVar
from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager

from fastapi import FastAPI, Request


LifespanDependency = Callable[[], AbstractAsyncContextManager[Any]]
# TODO: Allow dependencies to specify parameters in order to depend on each other
R = TypeVar("R")


class Lifespan:
    def __init__(self) -> None:
        self.dependencies: dict[str, LifespanDependency] = {}

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[Mapping[str, Any]]:
        state: dict[str, Any] = {}

        async with AsyncExitStack() as stack:
            for name, dependency in self.dependencies.items():
                state[name] = await stack.enter_async_context(dependency())

            yield state

    def register(
        self, dependency: Callable[[], AsyncIterator[R]]
    ) -> Callable[[Request], R]:
        self.dependencies[dependency.__name__] = asynccontextmanager(dependency)

        # TODO: figure out why @wraps(dependency) breaks `Depends()` usage
        def wrapped_dependency(request: Request) -> Any:
            # TODO: Class based dependencies don't have __name__ by default, so they'll probably break
            return request.state._state[dependency.__name__]

        return wrapped_dependency
