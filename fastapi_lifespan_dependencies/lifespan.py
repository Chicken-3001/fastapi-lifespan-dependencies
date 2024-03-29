from typing import Any, AsyncIterator, Callable, Mapping, TypeVar
from contextlib import AsyncExitStack, asynccontextmanager, AbstractAsyncContextManager

from fastapi import FastAPI, Request
from fastapi.requests import HTTPConnection
from fastapi.dependencies.utils import solve_dependencies, get_dependant

LifespanDependency = Callable[..., AbstractAsyncContextManager[Any]]
R = TypeVar("R")


class Lifespan:
    def __init__(self) -> None:
        self.dependencies: dict[str, LifespanDependency] = {}

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[Mapping[str, Any]]:
        state: dict[str, Any] = {}

        async with AsyncExitStack() as stack:
            for name, dependency in self.dependencies.items():
                dependant = get_dependant(path="", call=dependency)
                solved_values, *_ = await solve_dependencies(
                    request=Request(
                        scope={
                            # TODO: This might not work with websockets
                            "type": "http",
                            "query_string": "",
                            "headers": "",
                            "state": state,
                        }
                    ),
                    dependant=dependant,
                    async_exit_stack=stack,
                )

                state[name] = await stack.enter_async_context(
                    dependency(**solved_values)
                )

            yield state

    def register(
        self, dependency: Callable[..., AsyncIterator[R]]
    ) -> Callable[[HTTPConnection], R]:
        # TODO: Add synchronous dependency support
        self.dependencies[dependency.__name__] = asynccontextmanager(dependency)

        # TODO: figure out why @wraps(dependency) breaks `Depends()` usage
        def path_dependency(connection: HTTPConnection) -> Any:
            # TODO: Class based dependencies don't have __name__ by default,
            # so they'll probably break
            return connection.state._state[dependency.__name__]

        return path_dependency
