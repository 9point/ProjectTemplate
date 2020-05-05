# CLI

This describes how to use / access the project via the cli. For the most,
this is a reference to cli commands and what they do, but there is also
some discussion around those commands. Currently, commands are run using
[Taskfile](https://github.com/go-task/task).

## Configuring CLI

Environment variables need to be properly configured for the CLI commands
to work properly. See `kube/deploy.yml` for the list of configurations.

## Commands

```bash
task info
```

Get some basic info about the project. This includes the project name,
container image name, etc...

```bash
task tasks ls
```

List all the tasks defined in this project.

```bash
task workflows ls
```

List all the workflows defined in this project.

```bash
task test
```

Run all unit tests.

```bash
task start-worker
```

This starts a worker process for the current project. The worker automatically
connects to the service and is ready to receive work to do. For more information
on workers, view the documentation on [Workers](./Worker.md).

```bash
task run {routine-identifier} --param1 value1 --param2 value2
```

This starts a local process for running the given routine. Note that this will
_not_ start a worker, but instead run the routine locally. This means that
all code for the routine and all sub-routines will be run on the local
device. When running locally, only a single process is created to run the
routine (in the context of python, this means that there will be no parallel
execution of routines (look at the [Global Interpreter Lock](https://wiki.python.org/moin/GlobalInterpreterLock))
for why this is the case.

In the future, there may be support for running multi-process local routines,
but this is a low-pri piece of work. Multi-process routines should be run on
a distributed cluster, not locally.
