# Unit

A unit is the _unit_ of execution. It is code that is running on a _single_
machine. Each unit is given a set of parameters, and can define a return
value.

The code that is being run by a unit is freely defined by the
programmer so, in theory, that programmer can write a unit to execute
code remotely or call services that do work on other machines. For all
intents and purposes, the code within the unit will be opaque from the
rest of the system. The actual code written within a unit will get run on
a single machine.
