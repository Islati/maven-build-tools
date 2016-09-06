import logging
import os
import click
import sys
import yaml
from simpleplugins import PluginManager, get_files_recursive

from craftbuildtools.operations import OperationPlugin
from craftbuildtools.data import Project, DEFAULT_CONFIGURATION

logger = logging.getLogger("craft-buildtools")

formatter = logging.Formatter('[%(asctime)s %(name)-12s] [%(levelname)-8s] :: %(message)s')
console_log_handler = logging.StreamHandler()
console_log_handler.setFormatter(formatter)
console_log_handler.setLevel(logging.DEBUG)

logger.addHandler(console_log_handler)
logger.setLevel(logging.WARN)

import simpleplugins

# Assign the simple-plugins log-level to be of the same we have!
simpleplugins.logger.setLevel(logger.level)


class CraftBuildToolsApplication(object):
    def __init__(self):
        self.plugin_manager = PluginManager()
        self.config = None
        self.projects = {}
        self.build_projects = []
        self.built_projects = []
        self.copied_files = []
        self.app_config_folder = os.path.expanduser("~/.craftbuildtools/")
        self.files_folder = os.path.join(self.app_config_folder, "files")
        self.projects_folder = os.path.join(self.app_config_folder, "projects")

        if not os.path.exists(self.app_config_folder):
            os.makedirs(self.app_config_folder)
            logger.debug("Created app config folder at %s" % self.app_config_folder)

        if not os.path.exists(self.files_folder):
            os.makedirs(self.files_folder)

        if not os.path.exists(self.projects_folder):
            os.makedirs(self.projects_folder)
            logger.debug("Created projects folder at %s" % self.projects_folder)

        self.config_location = os.path.join(self.app_config_folder, "config.yml")

        self.__init_config()

        self.__init_files_folder()

        self.__load_plugins()

        self.__load_projects()

    def __load_plugins(self):
        self.plugin_manager.register(directory=os.path.abspath(os.path.join(os.path.dirname(__file__), 'operations')),
                                     skip_types=[OperationPlugin])

    def __init_config(self):
        if not os.path.isfile(self.config_location):
            self.__create_config()

        self.__load_config()

    def __init_files_folder(self):
        if not os.path.exists(self.files_folder):
            os.mkdir(self.files_folder)
            logger.debug("Created the Files folder at %s" % self.files_folder)

    def get_jar_files(self):
        return get_files_recursive(self.files_folder, "*.jar")

    def __load_projects(self):
        # For some reason matching against .yml files doesn't work, so let's look for all files.
        project_config_files = get_files_recursive(self.projects_folder, match='*')

        # There's no projects files to load, so let's make a dummy file and save it.
        if len(project_config_files) == 0:

            # Call the add projects plugin to perform the operation for a
            self.plugin_manager.get_plugin("addproject_operation").perform()

            for project in self.projects:
                with open(os.path.join(self.projects_folder, '%s.yml' % project.name), 'w') as project_new_config_file:
                    yaml.dump(project.yaml(), project_new_config_file, default_flow_style=False)

                logger.debug("Created Project File %s.yml" % project.name)

        # Now we loop through all the files in the projects directory and load them!
        for project_config_file in project_config_files:
            project = None
            with open(project_config_file, 'r') as project_file:
                project = Project.load(project_file)

                if project.name in self.projects:
                    logger.warning("Duplicate Project found [%s]" % project.name)
                    continue
                self.projects[project.name] = project

        logger.debug("Loaded Projects [%s] from config folder." % ",".join(name for name in self.projects.keys()))

    def __create_config(self):
        if not self.config:
            self.config = DEFAULT_CONFIGURATION

            self.config['ftp-server']['ftp-host'] = click.prompt("FTP Hostname", default="HOST")
            self.config['ftp-server']['ftp-username'] = click.prompt("FTP Username", default="USERNAME")
            self.config['ftp-server']['ftp-password'] = click.prompt("FTP Password", default="PASSWORD")
            self.config['ftp-server']['remote-upload-directory'] = click.prompt("Remote Upload Directory",
                                                                                default="/Dev/plugins/")

        with open(self.config_location, 'w') as yaml_file:
            yaml.dump(self.config, yaml_file, default_flow_style=False)

        logger.debug("Configuration for CraftBuildTools has been saved at %s" % self.config_location)

    def __load_config(self):
        with open(self.config_location, 'r') as yaml_file:
            self.config = yaml.load(yaml_file)

    def save_project(self, project):
        with open(os.path.join(self.app_config_folder, '%s.yml' % project.name), 'w') as project_new_config_file:
            yaml.dump(project.yaml(), project_new_config_file, default_flow_style=False)


app = CraftBuildToolsApplication()


@click.group(chain=True, add_help_option=True)
def cli():
    """
    \b
    About CraftBuildTools
    ----------------
    A wonderful suite of commands and utilities used to aid
    your development with Minecraft Projects.


    \b
    Features
    --------
        * Project Manager (To cache your project Information)
        * Clean your old project builds, and prepare for the new!
        * Build your projects! Not one at a time, but multiple!
        * Copy your built projects to a specific location!
        * Upload your built projects to a remote FTP Server!
    \b
        * Create Projects from Templates
            Reduce the amount of time it takes for
            you to get coding by giving CraftBuildTools a template
            to create your new project by!
            It will handle the entire process for you.
\b
        * Plugin-Based design!
            Rip out and replace any parts of the suite
            you wish; Changing their functionality but still allowing
            the rest of the app to function as it should!
\b
        * Lightweight!
            This is a big key! Having a lightweight
            CLI tool allows you to have maximum productivity
            leaving the pre-project boilerplate, and post-build
            actions entirely up to this tool!
    """


@cli.command("projects", help="""
\b
    Perform operations on a project.
    Select one of the following options:
      - list
      - add
      - edit
      - remove
    """)
@click.argument("action", type=click.STRING, default=None, required=False)
def projects_command(action):
    plugins_by_action = {
        'list': app.plugin_manager.get_plugin('listprojects_operation'),
        'add': app.plugin_manager.get_plugin('addproject_operation'),
        'edit': app.plugin_manager.get_plugin('editproject_operation'),
        'remove': app.plugin_manager.get_plugin('removeproject_operation')
    }

    if action is None:
        while True:
            action = click.prompt("Choose an action to perform (list, add, edit, remove)")
            if action in plugins_by_action:
                break
            else:
                click.clear()
                click.echo("%s is not a valid action; Try again!" % action)

    plugin = plugins_by_action[action]
    plugin.perform()


@cli.command(help="Clean all those old project files, and builds! (Think: mvn clean)")
def clean():
    app.plugin_manager.get_plugin("clean_operation").perform()


@cli.command(help="Build your projects in succession")
@click.option('-p', '--project', "projects", metavar="<name>", multiple=True, help="Project(s) to build")
def build(projects):
    app.build_projects.clear()

    if "all" in projects:
        for name in app.projects.keys():
            app.build_projects.append(name)
    else:
        for build_name in projects:
            if build_name not in app.projects:
                logger.debug("No project with named %s exists" % build_name)
                continue

            app.build_projects.append(build_name)
            logger.debug("Projects '%s' is to be built!" % build_name)

    app.plugin_manager.get_plugin("build_operation").perform()


@cli.command(help="To be used after build; Copy your built project files to a specific location")
@click.option("-l", "--location", "location", type=click.Path(), default=app.files_folder,
              help="Location to copy the built files to.")
def copy(location):
    app.files_folder = os.path.expanduser(location)

    if not os.path.exists(app.files_folder):
        os.makedirs(app.files_folder)

    app.plugin_manager.get_plugin("copy_operation").perform()


@cli.command("upload", help="""
Enabled you to upload your projects to a remote FTP Server after they've been built!

If the options are not specified, default values will be polled from the application config.
""")
@click.option("--updateconfig", "updateconfig", type=click.BOOL, default=False,
              help="Save the configuration values to file, for re-use")
@click.option('-h', "host", type=click.STRING, default=app.config['ftp-host'], help="FTP Host Name", metavar="<host>")
@click.option('-u', "user", type=click.STRING, default=app.config['ftp-username'], help="FTP username",
              metavar="<user>")
@click.option('-p', "password", type=click.STRING, default=app.config['ftp-password'], help="FTP Password",
              metavar="<password>")
@click.option('-d', "directory", type=click.STRING, default=app.config['remote-upload-directory'],
              help="Remote Folder for Files", metavar="<directory>")
def upload(host, user, password, directory, updateconfig):
    if updateconfig:
        app.config['ftp-server']['ftp-host'] = host
        app.config['ftp-server']['ftp-host'] = user
        app.config['ftp-server']['ftp-password'] = password
        app.config['ftp-server']['remote-upload-directory'] = directory
        logger.info("Updated FTP Configuration to the options provided.")

    click.echo("Beginning Upload Operation!")

    app.plugin_manager.get_plugin("upload_operation").perform(host=host, user=user, password=password,
                                                              directory=directory)


@cli.command(help="Generate a new project from a template! Get to coding quicker!")
@click.option("-tp", "--template", "template", metavar="<name>", type=click.STRING, required=False,
              help="Template to create the project with")
@click.option("-tf", "--templatefolder", "templatefolder", type=click.Path(),
              default=os.path.join(app.app_config_folder, "templates/"), help="Path where the template is stored")
@click.option("--clone", "git_clone_repo", metavar="<git-repo>", type=click.STRING, required=False,
              help="Clone down a git repo and use that as a template")
def createproject(template=None, templatefolder=None, git_clone_repo=None):
    app.plugin_manager.get_plugin("createproject_operation").perform(
        template=template,
        templatefolder=templatefolder,
        git_clone_repo=git_clone_repo
    )
