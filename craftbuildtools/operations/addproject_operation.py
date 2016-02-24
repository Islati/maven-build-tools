import os
import yaml
from craftbuildtools.operations import OperationPlugin
from craftbuildtools.data import Project


class AddProjectOperation(OperationPlugin):
    def __init__(self):
        super(AddProjectOperation, self).__init__()
        self.name = "addproject_operation"
        self.description = "Add a project to be managed"

    def perform(self, *args, **kwargs):
        from craftbuildtools import app, logger

        projects_config_dir = os.path.join(app.app_config_folder, 'projects')
        project = Project.create_from_prompt()

        with open(os.path.join(projects_config_dir, "%s.yml" % project.name), "w") as project_new_config_file:
            yaml.dump(project.yaml(), project_new_config_file, default_flow_style=False)

        app.projects[project.name] = project
        logger.info("Project %s has been added to CraftBuildTools" % project.name)


add_project_operation_plugin = AddProjectOperation()
