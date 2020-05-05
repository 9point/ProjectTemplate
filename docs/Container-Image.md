# Container Image

For a project to run in a distributed environment, there needs to be a way
to package up the project and run it as a program. [Docker](https://www.docker.com/)
is a great framework for containerizing your program into images that can be run
on different infrastructure and [Kubernetes](https://kubernetes.io/) is a
great tool for orchestrating a collection of containers. This documentation
will assume you are already familiar with how both of these systems work.

## Container Images and Projects

Every project has a collection of container images. As of now, each container
image is a python program that can run the various tasks and workflows
associated with the project. You can think of a container image as a snapshot
of a project in time. When you write up the code for a project (all tasks
and workflows associated with that project), then deploy the project, the
following happens:

- The system runs through the project to discover any routines. Those routines
  are submitted to the service. The service then persists those routines and
  returns the persisted versions (which include added fields such as the
  database id).

- The entire project is packaged into a docker container. The docker container
  is tagged with the latest commit hash associated with the project. It is then
  deployed to a docker registry (currently only supporting docker hub).

- A metadata object associated with that container is submitted to the service.
  This includes information such as: the full container image name, including
  the commit hash, the project associated with the container, and the routines
  associated with that container.

Note that it is very important that the service knows which routines and which
versions of those routines are associated with a particular project. This is
because a service may decide it needs to run a particular version of a task.
It needs to know which containers to which it can delegate that work.

## Container Images and Workers

As stated above, you can think of a container image as a snapshot of a project
in time. It contains all the tasks, routines, and code associated with that
project. But a container image isn't just a collection of code. It needs a way
to _run_ that code. For this to work, every container includes a program to
start a worker. You can read more about workers and what they do
[here](./Worker.md). When a worker is started from a container image, it
sits idle until it receives instructions from the service to do work. The
service makes this decision based on the work needed to be done and based on
the work that particular worker is capable of doing. If a service decides
that it needs to run a particular version of a task, it will look for a worker
that is online that knows how to run that task and is not currently busy.

If, for example, you want to run a task from an older version, you need to
start a worker from a container that is registered under that older version.

The container image has commands to facilitate accessing and running that code
for the project. However, the container itself does not have everything needed
to run the code. In particular, there are configurations missing in every
container image which are essential for the container to run. These
configurations are not baked into the container for security reasons. In order
to run a container image, these configurations need to be provided either
in the form of environment variables or volumes.

## Container Images and Kubernetes

As stated above, a container image has missing configuration that are essential
for it to do anything: start a worker, run a routine, read / write data
to storage, communicate with the service, etc...

This is where kubernetes makes our lives easier. There is currently a deployed
Kubernetes cluster containing all the secrets and configurations needed for
any worker to do its work. In order to run these configurations, the container
needs to deployed to that cluster and the configurations / secrets need to
be properly mapped to the relevant container image configuration variables.

The `kube/` directory at the root of this project template contains all the
configurations for deploying a container image as a kubernetes resource (or
set of resources). For this to work, you need access to an actual kubernetes
cluster that has all the listed configurations and secrets defined.

## Future Directions

As work on this system progresses, there may be some rethinking of the
relationship between a project and a container image. Currently, because
all code is being written in python and a container image is just a snapshot
of all that code, the container image is a snapshot of a project in time.

However, as this system evolves, there may be the need, for example, to run
tasks and workflows that are defined in different languages.
