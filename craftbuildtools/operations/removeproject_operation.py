import os
import click
from craftbuildtools.operations import OperationPlugin
from craftbuildtools.data import Project


class RemoveProjectOperation(OperationPlugin):
    def __init__(self):
        super(RemoveProjectOperation, self).__init__()
        self.name = "removeproject_operation"
        self.description = "Remove a project from the management of CraftBuildTools"

    def perform(self, *args, **kwargs):

        projects = kwargs.pop('projects')
        projects_folder = kwargs.pop('projects_folder')
        project_name = kwargs.pop("project_name")
        if project_name is None:
            available_projects = [name for name in projects.keys()]

            while True:
                click.echo("Available Projects: %s" % ",".join(p for p in available_projects))
                project_name = click.prompt("Which project would you like to remove?", prompt_suffix=" ")
                if project_name in available_projects:
                    break
                else:
                    click.echo("%s is not a valid project!" % project_name)
                    click.clear()
                    click.echo("")

        project_info = projects[project_name]

        remove_project_file = click.prompt(text="Are you sure you want to remove the project '%s'?" % project_info.name,
                                           confirmation_prompt=True, type=click.BOOL, prompt_suffix=" ")

        if not remove_project_file:
            return

        import shutil

        os.remove(os.path.join(projects_folder, '%s.yml' % project_info.name))
        click.echo("Project '%s' file '%s.yml' has been removed." % (project_info.name, project_info.name))

        remove_project_source_files = click.prompt("Would you like to remove the project source files?",
                                                   type=click.BOOL, default=False)

        if remove_project_source_files:
            remove_projects = click.prompt(
                "Are you sure you want to remove the project files at (%s)?" % project_info.directory,
                type=click.BOOL, confirmation_prompt=True)

            if remove_projects:
                try:
                    shutil.rmtree(project_info.directory)
                    click.echo("Files at %s has been removed" % project_info.directory)
                except:
                    click.echo("Unable to locate project files. Nothing was removed.")


remove_project_operation_plugin = RemoveProjectOperation()
