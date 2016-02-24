from simpleplugins import Plugin


class OperationPlugin(Plugin):
    def __init__(self, **kwargs):
        super(OperationPlugin).__init__(**kwargs)
        self.command_delegate = None

    def perform(self, *args, **kwargs):
        raise NotImplementedError("Perform is not implemented in base class (OperationPlugin)")

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False
