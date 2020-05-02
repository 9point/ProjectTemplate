from utils.introspection.trace import trace


class WorkflowExecutable:
    """
    Represents the code that defines a Workflow. Executing this code within the
    right environment will generate an AST which can be used to define the
    workflow.
    """
    def __init__(self, name, run):
        self.e_type = 'Workflow'

        self.name = name
        self.run = run

    def __call__(self):
        with trace() as t:
            t.visit(self)
