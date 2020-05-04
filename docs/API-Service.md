# API Service

While a worker is running, it must constantly be communicating with the API
service, Even if the worker is running a task or workflow locally. The
following are some examples of work that is communicated between a worker
and the API service:

**From the Service**

- instructions of what task / workflow to start
- instructions of whether to stop working on a task
- input parameters for the work that needs to be done

**From the Worker**

- a status indicating that the worker is ready to receive work
- a status indicating that the worker has finished its current work
- outputs of the task that are completed by the worker
