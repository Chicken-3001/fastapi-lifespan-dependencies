from contextlib import AbstractAsyncContextManager, AsyncExitStack, asynccontextmanager
from typing import Any, AsyncIterator, Callable, Mapping

from fastapi import FastAPI
from fastapi.dependencies.utils import get_dependant, solve_dependencies
from starlette.requests import HTTPConnection, Request

from fastapi_lifespan_dependencies.exceptions import LifespanDependencyError

LifespanDependency = Callable[..., AbstractAsyncContextManager[Any]]


class Lifespan:
    def __init__(self) -> None:
        self.dependencies: dict[str, LifespanDependency] = {}

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[Mapping[str, Any]]:
        state: dict[str, Any] = {}

        async with AsyncExitStack() as stack:
            for name, dependency in self.dependencies.items():
                dependant = get_dependant(path="", call=dependency)
                initial_state_request = Request(
                    scope={
                        "type": "http",
                        "query_string": "",
                        "headers": "",
                        "state": state,
                    }
                )

                # TODO: Research the async_exit_stack parameter
                (
                    solved_values,
                    errors,
                    background_tasks,
                    *_,
                ) = await solve_dependencies(
                    request=initial_state_request,
                    dependant=dependant,
                    async_exit_stack=stack,
                )

                if background_tasks is not None:
                    raise LifespanDependencyError(
                        "BackgroundTasks are unavailable during startup"
                    )
                    # TODO: Throw a similar error for responses

                if len(errors) > 0:
                    raise LifespanDependencyError(errors)
                    # TODO: Normalize errors (see fastapi.routing:313)

                state[name] = await stack.enter_async_context(
                    dependency(**solved_values)
                )

            yield state

    def register[R](
        self, dependency: Callable[..., AsyncIterator[R]]
    ) -> Callable[[HTTPConnection], R]:
        self.dependencies[dependency.__name__] = asynccontextmanager(dependency)
        # TODO: figure out why @wraps(dependency) breaks `Depends()` usage

        def path_dependency(connection: HTTPConnection) -> Any:
            # TODO: Class based dependencies don't have __name__ by default,
            # so they'll probably break
            return getattr(connection.state, dependency.__name__)

        return path_dependency
