from utils import define
from .train import TModel, train


@define.workflow(name="simple_example.build")
async def build() -> TModel:
    print('workflow building')
    model = await train(epochs=100)
    return model
