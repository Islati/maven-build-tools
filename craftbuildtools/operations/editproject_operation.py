import copy
import os
import click
from craftbuildtools.operations import OperationPlugin
from craftbuildtools.data import Project


class EditProjectOperation(OperationPlugin):
    def __init__(self):
        super(EditProjectOperation, self).__init__()
        self.name = "editproject_operation"
        self.description = "Edit a projects information"

    def perform(self, *args, **kwargs):
        from craftbuildtools import app, logger

        project_name = kwargs.pop("project_name", None)
        if project_name is None:
            available_projects = [name for name in app.projects.keys()]

            while True:
                click.echo("Available Projects: %s" % ",".join(p for p in available_projects))
                project_name = click.prompt("Which project would you like to Edit?", prompt_suffix=" ")
                if project_name in available_projects:
                    break
                else:
                    click.echo("%s is not a valid project!" % project_name)
                    click.clear()
                    click.echo("")

        project_info = app.projects[project_name]

        new_info = copy.deepcopy(project_info)

        new_info.name = click.prompt(text="Project Name", default=project_info.name, type=click.STRING)

        new_info.directory = click.prompt(text="Project Directory", default=project_info.directory,
                                          type=click.STRING)

        new_info.target_directory = click.prompt(text="Project Target Directory",
                                                 default=project_info.target_directory, type=click.STRING)

        new_info.build_command = click.prompt(text="Build Command", default=project_info.build_command,
                                              type=click.STRING)

        save_changes = click.prompt("Save Changes?", confirmation_prompt=True, type=click.BOOL)

        if not save_changes:
            click.echo("Changes to Project %s have been disregarded" % project_info.name)
            return

        del app.projects[project_name]
        import shutil
        import yaml

        config_path = os.path.join(app.projects_folder, "%s.yml" % project_info.name)

        app.save_project(new_info)
        click.echo("Project Information has been Updated!")

        if new_info.name != project_info.name:
            shutil.move(config_path, os.path.join(app.projects_folder, "%s.yml" % new_info.name))
            click.echo(
                "Previous config file %s has been renamed to %s" % (
                    "%s.yml" % project_info.name, "%s.yml" % new_info.name)
            )


add_project_operation_plugin = EditProjectOperation()
