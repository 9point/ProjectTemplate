from utils import define
from .train import TModel, train


@define.workflow(name="simple_example.build")
async def build() -> TModel:
    model = await train(epochs=1000)
    return model
