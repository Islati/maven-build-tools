import os
from craftbuildtools import OperationPlugin


class CleanOperation(OperationPlugin):
    def __init__(self):
        super(CleanOperation, self).__init__()
        self.name = "clean_operation"
        self.description = "Rid yourself of those dirty old files and get some new ones"

    def perform(self, *args, **kwargs):
        from craftbuildtools import app, logger
        import click

        for project_jar in app.get_jar_files():
            os.remove(project_jar)
            click.echo("File %s has been removed" % os.path.basename(project_jar))


clean_operation_plugin = CleanOperation()
