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
        from craftbuildtools import app, logger
        import click

        for project_name in app.projects.keys():
            project = app.projects[project_name]
            click.echo(project)


list_projects_operation_plugin = ListProjectsPlugin()
