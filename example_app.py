from random import randint
from typing import Annotated
from fastapi import Depends, FastAPI

from fastapi_lifespan_dependencies import Lifespan

lifespan = Lifespan()


@lifespan.register
async def number():
    print("generating number...")
    yield randint(1, 10)
    print("cleaning up number...")


@lifespan.register
async def string():
    print("generating string...")
    yield f"hi there {randint(1, 10)}!"
    print("cleaning up string...")


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def test(
    number: Annotated[int, Depends(number)], string: Annotated[str, Depends(string)]
):
    return {"number": number, "string": string}
