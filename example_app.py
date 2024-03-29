from random import randint
from typing import Annotated, Any
from fastapi import Depends, FastAPI

from fastapi_lifespan_dependencies import Lifespan

lifespan = Lifespan()


def get_number_range() -> tuple[int, int]:
    print("running get_number_range")
    return 1, 10


def get_random(
    number_range: Annotated[tuple[int, int], Depends(get_number_range)],
) -> int:
    print("running get_random")
    return randint(*number_range)


@lifespan.register
async def number(rand: Annotated[int, Depends(get_random)]):
    print("generating number...")
    yield rand
    print("cleaning up number...")


@lifespan.register
async def string(number: Annotated[int, Depends(number)]):
    print("generating string...")
    yield f"hi there, {number}!"
    print("cleaning up string...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def example(
    number: Annotated[int, Depends(number)],
    string: Annotated[str, Depends(string)],
    dependency: Annotated[int, Depends(get_random)],
) -> dict[str, Any]:
    return {"number": number, "string": string, "dependency": dependency}
