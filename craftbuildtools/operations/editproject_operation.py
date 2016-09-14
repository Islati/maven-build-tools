import copy
import logging
import os
import click
from craftbuildtools.operations import OperationPlugin

logger = logging.getLogger("craft-buildtools")

class EditProjectOperation(OperationPlugin):
    def __init__(self):
        super(EditProjectOperation, self).__init__()
        self.name = "editproject_operation"
        self.description = "Edit a projects information"

    def perform(self, *args, **kwargs):
        projects = kwargs.pop('projects')
        projects_folder = kwargs.pop("projects_folder")

        if projects is None or len(projects) is 0:
            click.echo("There are currently no projects to edit")
            return

        project_name = kwargs.pop("project_name", None)
        if project_name is None:
            available_projects = [name for name in projects.keys()]

            while True:
                click.echo("Available Projects: %s" % ",".join(p for p in available_projects))
                project_name = click.prompt("Which project would you like to Edit?", prompt_suffix=" ")
                if project_name in available_projects:
                    break
                else:
                    click.echo("%s is not a valid project!" % project_name)
                    click.clear()
                    click.echo("")

        project_info = projects[project_name]

        new_info = copy.deepcopy(project_info)

        new_info.name = click.prompt(text="Project Name", default=project_info.name, type=click.STRING)

        new_info.directory = click.prompt(text="Project Directory", default=project_info.directory,
                                          type=click.STRING)

        new_info.target_directory = click.prompt(text="Project Target Directory",
                                                 default=project_info.target_directory, type=click.STRING)

        new_info.build_command = click.prompt(text="Build Command", default=project_info.build_command,
                                              type=click.STRING)

        save_changes = click.prompt("Save Changes?", confirmation_prompt=True, type=click.BOOL)

        return save_changes, new_info, project_info


edit_project_operation_plugin = EditProjectOperation()
