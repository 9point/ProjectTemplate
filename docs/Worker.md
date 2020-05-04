# Worker

A worker is a process that is executing a unit. A worker can only execute one
unit at a time. To run multiple units in parallel, multiple workers will be
needed.

A worker never decides what work to do on its own, but must receive
instructions about what work to execute. For the most part, these instructions
will be delegated from the [API service](./API-Service.md). The project
template also allows executing workers tasks and workflows on a worker
directly as follows:

```bash
python src/main.py run train_model --data /path/to/data --hyperparams /path/to/hyperparams.json

```

However, a better way to execute work is through the API service.
