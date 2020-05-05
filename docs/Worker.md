# Worker

A [Worker](./Worker.md) is some process associated with a project that is
capable of doing work (this includes running routines). A worker can only
work on a single [Unit](./Unit.md) at a time. To run multiple units in parallel,
multiple workers will be needed.

A worker never decides what work to do on its own, but must receive
instructions about what work to execute. For the most part, these instructions
will be delegated from the [API service](./API-Service.md).

## Starting a Worker

When a worker is started, the following happens:

- The worker opens a connection with the service. When that connection opens,
  it creates a channel where [Worker Directives](./Worker-Directives.md) can
  be sent back and forth between the worker and the service.

- The worker indicates to the service that it is ready to receive _work_. Work
  meaning instructions on which routines to run.

- While a worker has an open connection with the service, the service does
  repeated health checks on the worker. This is called a _heartbeat_. During
  those health checks, the worker also indicates its work status, which is
  almost always either `IDLE` (waiting for work to do) or `WORKING` (currently
  working on some routine).

## Worker Statuses

## Running a Routine without a Worker

```bash
python src/main.py run train_model --data /path/to/data --hyperparams /path/to/hyperparams.json

```
