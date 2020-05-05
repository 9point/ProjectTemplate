# Project Template

## Overview

This Project Template is a framework for easily developing, iterating, and
scaling machine learning projects and workflows. The core design principles
are as follows:

- The code that runs a project on a local machine is the same code that should
  execute across a distributed cluster of workers.

- Minimal interaction with infrastructure. This means being able to easily
  deploy code that has been locally tested and specify _in code_ important
  configurations such as the number of workers working on a distributed task.

- Work should be reproducible. When running an expensive task a second time,
  there is no need to redo the computations.

## Installation and Setup

- [Python](https://www.python.org/downloads/) version 3.7.4 or later
- [Nose](https://nose.readthedocs.io/en/latest/).
- [Taskfile](https://taskfile.dev/#/installation)

For CLI commands associated with this project, look at the documentation
[here](./docs/CLI.md).

## Docs

The full documentation is [here](./docs/README.md).

## GRPC

The protobuf definitions are copied from the ML API Service code. The ML API Service
is the source of truth for the protobuf definitions. These definitions should not be
modified here.

Python documentation for GRPC can be found [here](https://grpc.io/docs/quickstart/python/).
