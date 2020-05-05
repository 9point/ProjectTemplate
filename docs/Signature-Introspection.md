# Signature Introspection

Signature introspection is the process of figuring out the typing signatures
of routines (tasks and workflows). This process is important as it allows us
to pull these routines out of a python context and run them in other contexts.
For example, being able to call these routines in different programming
languages or define them in a user interface.

It's important to note that due to the complexity of the problem, signature
introspection will be a part of the system that will be under continuous
development. While the initial implementations may only provide very basic
introspection (support for primitive types like int and str plus support
for collection types like List and Dict), more complex features (generics,
subclassing, etc...) will come at a later time.