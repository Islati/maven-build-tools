import logging
import os
import yaml
from craftbuildtools.operations import OperationPlugin
from craftbuildtools.data import Project

logger = logging.getLogger("craft-buildtools")


class AddProjectOperation(OperationPlugin):
    def __init__(self):
        super(AddProjectOperation, self).__init__()
        self.name = "addproject_operation"
        self.description = "Add a project to be managed"

    def perform(self, *args, **kwargs):
        app_config_folder = kwargs.pop('config_location')

        if app_config_folder is None:
            logger.error("Unable to create project as application config folder is undefined.")
            return None

        projects_config_dir = os.path.join(app_config_folder, 'projects')
        project = Project.create_from_prompt()

        with open(os.path.join(projects_config_dir, "%s.yml" % project.name), "w") as project_new_config_file:
            yaml.dump(project.yaml(), project_new_config_file, default_flow_style=False)

        logger.info("Project %s has been created, returning for CraftBuildTools" % project)
        return project

add_project_operation_plugin = AddProjectOperation()
