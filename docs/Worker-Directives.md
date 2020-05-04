# Worker Directives

A Worker Directive is a communication payload between the Worker and the API
Service. Every directive has two important fields: `payloadKey` and `payload`.
The `payloadKey` is a string indicating the type of directive being sent, and
a `payload` is a json object containing the information being communicated.

The following are all the directives being sent between worker and service:

**From Worker**

`v1.heartbeat.give_pulse`

`v1.ready`

`v1.log`

**From Service**

`v1.heartbeat.check_pulse`

`v1.task.request_start`
