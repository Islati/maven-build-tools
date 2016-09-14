from craftbuildtools.operations import OperationPlugin


class ListProjectsPlugin(OperationPlugin):
    def __init__(self):
        super(ListProjectsPlugin, self).__init__()
        self.name = "listprojects_operation"
        self.version = "1",
        self.description = "List all the available projects to perform operations upon"

    def activate(self):
        pass

    def deactivate(self):
        pass

    def perform(self, *args, **kwargs):
        projects = kwargs.pop('projects')
        import click

        if projects is None or len(projects) is 0:
            click.echo("No projects to list.")
            return

        for project in projects:
            click.echo(project)

list_projects_operation_plugin = ListProjectsPlugin()
