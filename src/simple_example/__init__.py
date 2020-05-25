import asyncio

from utils import define
from .train import TModel, train


@define.workflow(name="simple_example.build")
async def build() -> str:
    model = await asyncio.gather(train(epochs=10),
                                 train(epochs=10),
                                 train(epochs=10))

    return 'Done with mode result'
