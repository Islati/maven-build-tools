import logging
import os
import click
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
            click.echo("Created app config folder at %s" % self.app_config_folder)

        if not os.path.exists(self.files_folder):
            os.makedirs(self.files_folder)

        if not os.path.exists(self.projects_folder):
            os.makedirs(self.projects_folder)
            click.echo("Created projects folder at %s" % self.projects_folder)

        self.config_location = os.path.join(self.app_config_folder, "config.yml")

        self.__init_config()

        self.__init_files_folder()

        self.__load_plugins()

        self.__load_projects()

    def __load_plugins(self):
        self.plugin_manager.register(directory=os.path.abspath(os.path.join(os.path.dirname(__file__), 'operations')),
                                     skip_types=[OperationPlugin])

        logger.debug("Registered %s plugins for the Plugin Manager" % len(self.plugin_manager.plugins))

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
            project = self.plugin_manager.get_plugin("addproject_operation").perform(
                config_location=self.app_config_folder)

            self.projects[project.name] = project

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

        logger.debug("Loaded Projects [%s] from config folder." % ",".join(name for name in list(self.projects.keys())))

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

        click.echo("Configuration for CraftBuildTools has been saved at %s" % self.config_location)
        # logger.debug("Configuration for CraftBuildTools has been saved at %s" % self.config_location)

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
    plugins_by_action = [
        'list',
        'add',
        'edit',
        'remove',
    ]

    if action is None:
        while True:
            action = click.prompt("Choose an action to perform (list, add, edit, remove)")
            if action in plugins_by_action:
                break
            else:
                click.clear()
                click.echo("%s is not a valid action; Try again!" % action)

    if action == "add":
        app.plugin_manager.get_plugin('addproject_operation').perform(config_location=app.config_location)
    elif action == "list":
        app.plugin_manager.get_plugin('listprojects_operation').perform(
            projects=[project for project in list(app.projects.values())])
    elif action == "edit":
        save, new_info, old_info = app.plugin_manager.get_plugin('editproject_operation').perform(projects=app.projects,
                                                                                                  projects_folder=app.projects_folder)

        if save is False:
            click.echo("Changes for the project have been disregarded")
            return

        del app.projects[old_info.name]

        import shutil

        config_path = os.path.join(app.projects_folder, "%s.yml" % old_info.name)

        app.save_project(new_info)
        click.echo("Project Information has been Updated!")

        if new_info.name != old_info.name:
            shutil.move(config_path, os.path.join(app.projects_folder, "%s.yml" % new_info.name))
            click.echo(
                "Previous config file %s has been renamed to %s" % (
                    "%s.yml" % old_info.name, "%s.yml" % new_info.name)
            )

        app.projects[new_info.name] = new_info

    elif action == "remove":
        app.plugin_manager.get_plugin('removeproject_operation').perform(projects=app.projects,
                                                                         projects_folder=app.projects_folder)


@cli.command(help="Clean all those old project files, and builds! (Think: mvn clean)")
def clean():
    app.plugin_manager.get_plugin("clean_operation").perform(jar_files=app.get_jar_files())


@cli.command(help="Build your projects in succession")
@click.option('-p', '--project', "projects", metavar="<name>", multiple=True, help="Project(s) to build", required=True)
def build(projects):
    build_projects = []

    if "all" in projects:
        for name in list(app.projects.keys()):
            build_projects.append(name)
    else:
        for build_name in projects:
            if build_name not in app.projects:
                click.echo("No project with named %s exists" % build_name)
                continue

            build_projects.append(build_name)
            click.echo("Projects '%s' is to be built!" % build_name)

    successful_builds, failed_builds = app.plugin_manager.get_plugin("build_operation").perform(
        build_projects=build_projects, projects=app.projects
    )

    if successful_builds is None or failed_builds is None:
        return

    app.built_projects = [app.projects[project.name] for project in successful_builds]


@cli.command(help="To be used after build; Copy your built project files to a specific location")
@click.option("-l", "--location", "location", type=click.Path(), default=app.files_folder,
              help="Location to copy the built files to.")
def copy(location):
    app.files_folder = os.path.expanduser(location)

    if not os.path.exists(app.files_folder):
        os.makedirs(app.files_folder)

    copied_files = app.plugin_manager.get_plugin("copy_operation").perform(built_project=app.built_projects,
                                                                           files_folder=app.files_folder)

    app.copied_files = copied_files


@cli.command("upload", help="""
Enabled you to upload your projects to a remote FTP Server after they've been built!

If the options are not specified, default values will be polled from the application config.
""")
@click.option("--updateconfig", "updateconfig", type=click.BOOL, default=False,
              help="Save the configuration values to file, for re-use")
@click.option('-h', "host", type=click.STRING, default=app.config['ftp-server']['ftp-host'], help="FTP Host Name",
              metavar="<host>")
@click.option('-u', "user", type=click.STRING, default=app.config['ftp-server']['ftp-username'], help="FTP username",
              metavar="<user>")
@click.option('-p', "password", type=click.STRING, default=app.config['ftp-server']['ftp-password'],
              help="FTP Password",
              metavar="<password>")
@click.option('-d', "directory", type=click.STRING, default=app.config['ftp-server']['remote-upload-directory'],
              help="Remote Folder for Files", metavar="<directory>")
def upload(host, user, password, directory, updateconfig):
    if updateconfig:
        app.config['ftp-server']['ftp-host'] = host
        app.config['ftp-server']['ftp-host'] = user
        app.config['ftp-server']['ftp-password'] = password
        app.config['ftp-server']['remote-upload-directory'] = directory
        click.echo("Updated FTP Configuration to the options provided.")

    click.echo("Beginning Upload Operation!")

    app.plugin_manager.get_plugin("upload_operation").perform(
        host=host.user,
        user=user,
        password=password,
        directory=directory,
        copied_files=app.copied_files,
        jar_files=app.get_jar_files()
    )


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
        git_clone_repo=git_clone_repo,
        plugin_manager=app.plugin_manager
    )
