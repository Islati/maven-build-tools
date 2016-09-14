import logging
import os
from craftbuildtools.operations import OperationPlugin

logger = logging.getLogger("craft-buildtools")



class CleanOperation(OperationPlugin):
    def __init__(self):
        super(CleanOperation, self).__init__()
        self.name = "clean_operation"
        self.description = "Rid yourself of those dirty old files and get some new ones"

    def perform(self, *args, **kwargs):
        import click

        files = kwargs.pop('jar_files')
        for project_jar in files:
            os.remove(project_jar)
            click.echo("File %s has been removed" % os.path.basename(project_jar))


clean_operation_plugin = CleanOperation()
