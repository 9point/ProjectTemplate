# Routine Engine

Routines are defined in some code that exists within the project. At some point,
that code needs to run, usually either within the context of a worker executing
a unit of work or a local job running on a single machine.

In any case, there is a lot of support needed for a routine to run and
execute properly. Here are some examples of things that need to be managed
by the runtime.

- When a task or workflow is completed, the results need to be stored
  somewhere. Location of storage needs to be aware of the specific task that
  completed and the version of that task.

- When a task is started, there may be cases where we can avoid running the
  code. If we have run the same version of the task at some other point in the
  past, then we would like to simply return the results from a previous run.
  Tasks are expected to be pure, deterministic, and have no side effects. Look
  through the documentation on [tasks](./Task.md) for more information.

- Send directives to the service to complete sub-routines like tasks on other,
  remote workers.

- Run a Routine Trigger when a routine has completed (this is not yet supported
  and is listed as a [future feature](./Routine-Triggers.md)).

The job of the _Routine Engine_ is to handle all the specifics of these cases.
The actual engine is tucked away and the user should not need to interact with
it directly, but under the hood, it does all the heavy lifting and plays an
important role in keeping the code required for running routines simple.

## Local Engine

Consider the following code to run and wait for the results of a task:

```python

@define.task(name="train", version="0.0.1")
def train(data: Data, epochs: int, hyperparams: List[HyperParams]) -> List[Model]:
  # Do the training here, then return the list of models.


async def do_stuff():
  hyperparams = [dict(lr=0.1), dict(lr=0.01), dict(lr=0.001)]
  data = get_data()
  epochs = 100
  models = await train(data, epochs, hyperparams)

```

Imagine running this code as a local python script / job (not on a distributed
workflow). For routines that are running locally, a `LocalRunEngine` is
instantiated and manages the process of running the above code. When the
`LocalRunEngine` is active, the following happens when executing a routine:

- Check the storage to see if this task was ever run before with the same
  parameters. If it has, instead of running this code, just return the results
  that have been stored.

- Call the routine as a python co-routine.

- When the co-routine is complete, store the results of the task in storage.

- Return the results.

The `LocalRunEngine` is a light-weight wrapper over the routine that's running.
It doesn't do much other than interact with storage. This is the simplest type
of engine that exists.
