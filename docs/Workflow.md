# Workflow

A workflow orchestrates the running of a collection of workflows and tasks.
Workflows are therefore recursively defined since they can have other workflows
within them. A Workflow can be thought of as a program where the subroutines
are tasks and other workflows. Those subroutines can be run in parallel or
one could wait for the execution of one or more subroutines before beginning
a new subroutine.

## Defining a Workflow

```python
import asyncio

from typing import Any, List, TypedDict
from utils import define

HyperParams = TypedDict('HyperParams', lr=float, num_layers=int)
MyModel = Any
Data = Any

@define.workflow(name="train_and_pick_model")
async def train_and_pick_model(data: Data, hyperparams: List[HyperParams]) -> MyModel:
    train_awaitables = [train_model(data=data, lr=hp['lr'], num_layers=hp['num_layers']) for hp in hyperparams]
    models = await asyncio.gather(train_awaitables)
    return await find_best_model(models)


@define.task(name="train_model", version="0.0.1")
def train_model(data: Data, hyperparams: HyperParams) -> MyModel:
    # Code here to train a model.


@define.task(name="find_best_model", version="0.0.1")
def find_best_model(models: List[MyModel]) -> MyModel:
    # Code here to find the best model.

```

The awesome thing about this code is that it works on your local machine
as well as in a distributed environment. You can run it locally by calling
the workflow, or you can deploy it to a multi-node cluster and have those
tasks operate on a distributed system.

Running the above code locally:

```python
import asyncio

hyperparams = [
  dict(lr=0.01,  num_layers=2),
  dict(lr=0.001, num_layers=2),
  dict(lr=0.01,  num_layers=4),
  dict(lr=0.001, num_layers=4),
]

model = await train_and_deploy_model(data, hyperparams)

```

## Workflow Unique Identifier

Workflows can be identified in one of two ways. Depending on the
particular context you are running, usually one of the identifiers are
more convenient to use.

- Using the workflow name and revision number:
  `{workflow-name}:{revision-number}`. Note that this is uniquely only within
  the context of a particular project. To make this globally unique, you can
  include the project name: `{project-name}:{workflow-name}:{revision-number}`.
  Note also that in some contexts, just the workflow name is enough. When this
  identifier is used, the system will do its best to fill in the missing
  information from the runtime context. If more information than needed is
  given (such as including the project name when the project name is
  already known), then that is fine, as long as the information is
  correct (providing the incorrect project name for a runtime where the project
  name is already known will result in an identification failure).

- Use the database id for the workflow. All database ids are globally unique.
