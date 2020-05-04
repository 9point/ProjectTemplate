# Tasks

A task is a unit or collection of units that are running simultaneously.
A task can run a single unit or a collection of units, all of which are
running in parallel. When the task is complete, all the units within the task
are also complete. A task is associated with a version.

## Defining a Single-Unit Task

Defining a task can be as follows:

```python
from typing import List
from utils import define

@define.task(name="sort", version="0.0.1")
def sort(list: List[float]) -> List[float]:
    return sorted(list)

```

When a task is defined using the `@define.task` decorator, the task is wrapped
in an [asyncio](https://docs.python.org/3/library/asyncio.html) context. To
use the task, you must execute it as follows:

```python
sorted_list = await sort([3, 2, 1])
```

Some requirements for tasks:

- The task should block until it is complete. When the task returns, the
  system assumes that all the work for that task is done.

- A task must use the python [typing](https://docs.python.org/3/library/typing.html) semantics.

- A task should not rely on side effects to manipulate parameters. Performing
  side effects on the input parameters will not be properly understood
  semantically by workflows or the distributed system.

## Task Name and Version

When defining a task, that task is given a name and semver version. The name
of the task must be unique among all tasks and workflows across the project.

## Define a Multi-Unit Task

TODO: Take a deeper look into the python multi-threading api. Would like
to make the multi-unit api as similar as possible to managing multiple threads.

To define a task with multiple units, you must set the multiple units flag:

```python
from typing import List
from utils import define
from utils.types import MultiUnitAPI

@define.task(name="sort", version="0.0.1", multi_units=True, unit_count=range(5))
async def sort(api: MultiUnitAPI[List[float], List[float]]) -> None:
    # If this is the master unit, fetch the full list and partition into
    # smaller lists to get processed by sub-units.
    if api.rank == 0:
        full_list = await api.receive_input()
        sub_lists = perform_partition(full_list, api.unit_count)

        my_list = sub_lists[0]
        other_lists = sub_lists[1:]

        for i in range(1, len(sub_lists)):
            api.send(rank=i, key='my_list', args=(sub_list,))

    # If this is the slave unit, it received the sublist from the master.
    # Note here that the slave list is not receiving the inputs directly,
    # but instead is receiving the sublist.
    else:
        my_list = await api.receive(rank=0, key='my_list')


    sorted_list = sorted(my_list)

    # The master process waits for all other units to finish sorting the list,
    # then merges each of the results into a master list. It then sends the
    # result of this to the output.
    if api.rank == 0:
        other_sorted_lists = await api.receive_many(ranks=range(1, len(sub_lists)), key='sorted')
        master_sorted_list = merge(my_list, *other_sorted_lists)
        api.send_output(master_sorted_list)

    # The slave list sends its sorted list.
    else:
        api.send(rank=0, key='sorted', sorted_list)

```

By making a task work across units, the following changes are made:

- A multi-unit task has one input, which is an api module. This module has
  generic types TInput and TOutput.

- The unit receives parameter inputs through the `receive_input` method and
  sends outputs through the `send_output` method.

- The unit can use helper methods on the api to coordinate work among the the
  different units.

Some important things to consider:

- Every unit is given a rank. Only the unit with `rank=0` may send the output.
  If any other unit tries to sends output, this will be considered an error.

- A multi-unit task takes a single input and returns a single output. If you
  want to use multiple inputs for a task, you can wrap them in an object.
