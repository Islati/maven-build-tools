#!/usr/bin/python3
import fnmatch
import yaml
import os
import shutil
import argparse
import subprocess
import logging
import click

try:
    from sh import git
except ImportError:
    print("Unable to locate the git executables on your system. Please assure you have git installed and try again!")
    exit()

from logging.config import dictConfig
from builtins import input
from bs4 import BeautifulSoup
from ftpretty import ftpretty
from cookiecutter.main import cookiecutter

# TODo Eventually make it able to scan for projects based on where they're stored!
# TODO Implement FTP output to server with directory

parser = argparse.ArgumentParser(description="Options to run CraftBuildTools By")
parser.add_argument('--copy', required=False, action="store_true", help="Copy Files Flag")
parser.add_argument('--location', required=False,
                    help="If the copy flag is included, this will output them to an optional location.")
parser.add_argument('--clean', required=False, action='store_true',
                    help='Clear all files currently here before copying')
# parser.add_argument('--config', required=False, type=argparse.FileType)
parser.add_argument('--build', required=False, nargs="*", default=None)
# parser.add_argument('--build', required=False, action="store_true")
# TODO Create an argument group for adding projects, with sub args dependant on how its structured
parser.add_argument('--addproject', action="store_true", required=False,
                    help='Directories of Maven projects which to add!')
parser.add_argument('--createproject', action="store_true", required=False,
                    help="Create a new Maven project for your Minecraft Project!")
parser.add_argument('--todo', required=False, action="store_true", help="Flag used to generate the todo file")
parser.add_argument('--upload', required=False, action="store_true",
                    help="Whether or not to upload the files to the server.")
parser.add_argument('--remotefolder', required=False, help="The remote location which to upload files to!")
parser.add_argument('--listprojects', required=False, action="store_true",
                    help="List all the available projects to perform operations on!")
parser.add_argument('--verbose', required=False, action="store_true",
                    help="Verbose output! Maximize the output given by CraftBuildTools")
parser.add_argument('--commons', required=False, action='store_true',
                    help='When this flag is enabled, executing craft build tools will simply clone Commons, its dependencies, build it using maven, add it to your project structure, and then prep for the next execution; Commons is a massive bukkit framework used to ease the development of plugins for servers, and ease the hosting of servers for owners. It\'s a win win! If you plan on using Commons its\'s highly suggested to run this before continueing.')

args = None

# TODO Make some implementation of the mary jane.

# TODO Implement option to run tools.py --build [projects-name] --copy [Name [Name]]

# TODO Implement option to create bukkit / spigot projects with dependancies and so forth; Commons, Vault, Etc.

logging_config = dict(
    version=1,
    formatters={
        'log_format': {'format': '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'},
    },
    handlers={
        'stream_handler': {
            'class': 'logging.StreamHandler',
            'formatter': 'log_format',
            'level': logging.DEBUG
        },
        # 'file_handler': {
        #     'class': 'logging.FileHandler',
        #     'formatter': 'log_format',
        #     'filename': 'builds.log',
        #     # os.path.join(os.path.dirname(os.path.realpath(__file__)), "/logs/","%s.log" % time.strftime("%H-%M-%S")),
        #     'level': logging.DEBUG
        # }
    },
    loggers={
        'root': {
            'handlers': ['stream_handler'
                         # , 'file_handler'
                         ],
            'level': logging.DEBUG
        }
    }
)

dictConfig(logging_config)

logger = logging.getLogger(name="Builds Logger")


def get_files_recursive(path, match='*.py'):
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, match):
            matches.append(os.path.join(root, filename))

    return matches


class ChangeDir:
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    # Change directory with the new path
    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    # Return back to previous directory
    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class Project(object):
    def __init__(self, name, directory, target_directory, build_command="mvn clean install"):
        self.name = name
        self.directory = directory
        self.target_directory = target_directory
        self.build_command = build_command

    def yaml(self):
        return {
            'name': self.name,
            'directory': self.directory,
            'target_directory': self.target_directory,
            'build_command': self.build_command
        }

    @classmethod
    def create_from_prompt(cls):
        print("Please enter your project information!")
        name = input("Project Name: ")
        directory = input("Project Directory: ")
        target_directory = input("Project Build Directory: ")
        build_command = input("Project Build Command: ")
        return Project(name=name, directory=directory, target_directory=target_directory, build_command=build_command)

    @staticmethod
    def load(data):
        values = yaml.safe_load(data)
        return Project(
            name=values['name'],
            directory=values['directory'],
            target_directory=values['target_directory'],
            build_command=values['build_command']
        )

    def __get_pom_file(self):
        pom_path = os.path.join(self.directory, "pom.xml")
        if not os.path.exists(pom_path):
            print("Project %s has no pom.xml at expects '%s'" % (self.name, pom_path))
            return None

        return pom_path

    def __has_pom_file(self):
        return self.__get_pom_file() is not None

    def get_pom_info(self):
        pom_file = self.__get_pom_file()
        if pom_file is None:
            print("Unable to find pom file for project %s" % self.name)
            return None

        pom_doc = None
        with open(pom_file, 'r') as pom_xml_file:
            pom_doc = pom_xml_file.read()

        if pom_doc is None:
            return None

        soup = BeautifulSoup(pom_doc, 'lxml')

        has_parent = len(soup.find_all("parent")) > 0

        artifact_id = None
        version = None
        if has_parent:
            art_count = 0
            for artifact_ids in soup.find_all("artifactid"):
                if art_count == 0:
                    art_count += 1
                    continue
                else:
                    artifact_id = artifact_ids.string
                    break

            ver_count = 0
            for versions in soup.find_all("version"):
                if ver_count == 0:
                    ver_count += 1
                    continue
                else:
                    version = versions.string
                    break

        else:
            artifact_id = soup.find("artifactid").string
            version = soup.find('version').string

        output_jar = "%s-%s.jar" % (artifact_id, version)

        # TODO parse more pom info.
        return {
            'output_jar': output_jar,
            'version': version,
            'artifact_id': artifact_id
        }

    def get_files(self, match="*.*"):
        return get_files_recursive(self.directory, match=match)

    def build(self):
        build_success = False
        with ChangeDir(self.directory):
            print("Executing build command '%s' on Project %s" % (self.build_command, self.name))

            # TODO Implement timer to see how long build starts, or spawn in a subprocess.

            build_process = subprocess.Popen(self.build_command, shell=True, stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT)

            maven_build_lines = []
            for line in build_process.stdout.readlines():
                maven_build_lines.append(line)

                if args.verbose:
                    print(line)

            build_value = build_process.wait()

            build_success = any(b"BUILD SUCCESS" in line for line in maven_build_lines)

            if build_success is True:
                print("Project %s has been built successfully" % self.name)
            else:
                print("Project %s has failed to build" % self.name)
        return build_success

    def __str__(self):
        return """*-- %s --*
    * Directory: %s
    * Build Command %s
    * Version: %s
        """ % (
            self.name,
            self.directory,
            self.build_command,
            self.get_pom_info()['version']
        )

    def __repr__(self):
        return self.__str__()


class ToDo(object):
    def __init__(self):
        pass


class ToDoManager:
    def __init__(self):
        pass


class App:
    def __init__(self, args):
        self.config = None

        self.projects = []

        self.build_projects = []

        self.verbose = args.verbose

        # Todo Move operations to classes that are executed with args.
        self.operations = {
            'copy': args.copy,
            'clean': args.clean,
            'build': args.build is not None,
            # 'build':  args.build,
            'todo': args.todo,
            'add_project': args.addproject,
            'upload': args.upload,
            'create_project': args.createproject,
            'list_projects': args.listprojects,
            'commons': args.commons
        }

        self.config_folder = os.path.expanduser("~/.craftbuildtools/")

        if not os.path.exists(self.config_folder):
            os.makedirs(self.config_folder)

        self.config_location = os.path.join(self.config_folder, "config.yml")

        # Load the configuration file.
        self.__init_config()

        # The files folder, which will contain all the files generated by build / copy operations.
        if args.location is not None:
            self.files_folder = args.location
            print("Updated output folder to %s" % args.location)
        else:
            self.files_folder = os.path.join(self.config_folder, "files")

        # Create the files folder (Where all the copied jar files will be going!
        self.__init_files_folder()

        # If they've put in the remote upload directory, then save that to the config file!
        if args.remotefolder:
            self.config['remote-upload-directory'] = args.remotefolder
            print("Remote upload directory has been changed to %s" % args.remotefolder)
            self.__create_config()

        self.__load_projects()

        if args.build is not None:
            if "all" in args.build:
                self.build_projects.append("all")
            else:
                for project_name in args.build:
                    self.build_projects.append(project_name)
        else:
            print("Skipping implementation of build process!")

    def __init_files_folder(self):
        if not os.path.exists(self.files_folder):
            os.mkdir(self.files_folder)
            print("Created the Files folder at %s" % self.files_folder)

    def __get_jar_files(self):
        return get_files_recursive(self.files_folder, "*.jar")

    def __load_projects(self):
        projects_config_dir = os.path.join(self.config_folder, 'projects')

        # Create the projects folder if it doesn't exist.
        if not os.path.exists(projects_config_dir):
            os.mkdir(projects_config_dir)
            print("Created projects folder @ %s" % projects_config_dir)

        # For some reason matching against .yml files doesn't work, so let's look for all files.
        project_config_files = get_files_recursive(projects_config_dir, match='*')

        # There's no projects files to load, so let's make a dummy file and save it.
        if len(project_config_files) == 0:
            # Prompt the user for a project and it's information!
            self.projects.append(
                Project.create_from_prompt()
            )

            for project in self.projects:
                with open(os.path.join(projects_config_dir, '%s.yml' % project.name), 'w') as project_new_config_file:
                    yaml.dump(project.yaml(), project_new_config_file, default_flow_style=False)

                print("Created Project File %s.yml" % project.name)

        # Now we loop through all the files in the projects directory and load them!
        for project_config_file in project_config_files:
            project = None
            with open(project_config_file, 'r') as project_file:
                project = Project.load(project_file)

                if project in self.projects:
                    print("Duplicate Project found [%s]" % project.name)
                    continue
                self.projects.append(project)

        print("Loaded Projects [%s] from config folder." % ",".join(project.name for project in self.projects))

    def __init_config(self):
        if not os.path.isfile(self.config_location):
            self.__create_config()

        self.__load_config()

    def __create_config(self):
        # TODO Modify this to do some useful or somethin.
        if not self.config:
            self.config = {
                'ftp-host': 'HOST',
                'ftp-username': 'USERNAME',
                'ftp-password': 'PASSWORD',
                'remote-upload-directory': '/Dev/plugins/'
            }

        with open(self.config_location, 'w') as yaml_file:
            yaml.dump(self.config, yaml_file, default_flow_style=False)

        print("Configuration for CraftBuildTools has been saved at %s" % self.config_location)

    def __load_config(self):
        with open(self.config_location, 'r') as yaml_file:
            self.config = yaml.load(yaml_file)

    def save_project(self, project):
        projects_config_dir = os.path.join(self.config_folder, 'projects')

        with open(os.path.join(projects_config_dir, '%s.yml' % project.name), 'w') as project_new_config_file:
            yaml.dump(project.yaml(), project_new_config_file, default_flow_style=False)

    def run(self):

        if self.operations['commons']:
            commons_repo_url = click.prompt("Commons Git Repository",
                                            default="https://github.com/TechnicalBro/Commons.git")
            clone_repo_dir = os.path.expanduser(click.prompt("Directory for Repository", default="~/Projects"))
            commons_repo_dir = os.path.join(clone_repo_dir, "Commons")

            if not os.path.exists(clone_repo_dir):
                print("Folder to clone your repo into doesn't exists.")
                create_parent_dir = click.prompt("Create the parent folder for Commons Repository", type=click.BOOL,
                                                 default=True)
                if not create_parent_dir:
                    print("Unable to continue forward with operations as we're unable to create the parent directory.")
                    return

                os.makedirs(clone_repo_dir)
                print("Created the parent directory which Commons will be stored in.")
                print("Just one moment, preparing project for cloning.")

            if os.path.isdir(commons_repo_dir):
                delete_existing_repo = click.prompt("Delete existing Commons project", type=click.BOOL,
                                                    default=False)
                if not delete_existing_repo:
                    print("Cancelled. Not removing the current Commons project files.")
                    exit()
                    return
                else:
                    shutil.rmtree(commons_repo_dir)
                    print("Removed the existing Commons data.")

            with ChangeDir(clone_repo_dir):
                print("Changed active directory to %s for cloning to")
                print("Beginning to clone Commons repository from: %s" % commons_repo_url)
                git.clone(commons_repo_url)

                new_repo_exists = os.path.exists(commons_repo_dir)
                if not new_repo_exists:
                    print(
                        "After attempting to clone the Commons repository, operations have failed. Exiting CraftBuildTools")
                    exit()
                    return

                print("Successfully cloned %s to %s" % (commons_repo_url, commons_repo_dir))
                print("Creating a CraftBuildTools project file for Commons.")
                commons = Project(
                    name="Commons",
                    directory=commons_repo_dir,
                    target_directory=os.path.join(commons_repo_dir, 'target')
                )

                self.save_project(project=commons)
                print("Saved Commons to the CraftBuildTools configuration directory.")
                print("Attempting to build Commons using maven, and build commons '%s'" % commons.build_command)
                if not commons.build():
                    print(
                        "Unable to build Commons maven project. Execute a manual maven build to determine the error. Sorry. :(")
                    return

                print(
                    "You've built Commons successfully! Congratulations, you're now able to make awesome Bukkit Plugins!")
                return

        if self.operations['list_projects']:
            for project in self.projects:
                print(project.__str__())
            return

        if self.operations['create_project']:

            templates_folder = os.path.join(self.config_folder, "templates")

            if not os.path.exists(templates_folder):
                os.makedirs(templates_folder)
                with ChangeDir(templates_folder):
                    print("Cloning CookieCutter Template: Commons (BukkitPlugin)")
                    git.clone('https://github.com/TechnicalBro/cookiecutter-commons-bukkitplugin.git')
                    print("Finished Cloning.")
                    print("Cloning CookieCutter Template: Commons (MiniGame)")
                    git.clone("https://github.com/TechnicalBro/cookiecutter-commons-minigame.git")
                    print("Finished Cloning.")
                    # TODO implement argparse arg for adding more repos / templates.


            # todo move prompting to click prompt.
            project_author = click.prompt("Project Author", default="Your Username")
            project_name = click.prompt("Project Name", default="My Spigot Project")
            project_version = click.prompt("Project Version", default="1.0.0")
            project_description = click.prompt("Project Description", default="A cookie-cutter spigot project")

            plugin_types = ['BukkitPlugin', 'MiniGame']
            choice_lines = ["{}".format(plugin_type) for plugin_type in plugin_types]

            plugin_type_prompt = "Plugin Type - Choose from ({})".format(', '.join(choice_lines))

            plugin_type = click.prompt(plugin_type_prompt, type=click.Choice(plugin_types), default='BukkitPlugin')

            main_package = click.prompt("Main Package",
                                        default="com.caved_in.%s" % project_name.lower().replace(' ', '_').replace('-',
                                                                                                                   '_'))

            main_class = click.prompt(
                "Main Class", default=project_name.replace(' ', '').replace("-", ""))

            user_class = ""
            user_manager_class = ""
            if plugin_type == "MiniGame":
                user_class = click.prompt("User Class", default="%sUser" % main_class)
                user_manager_class = click.prompt("User Manager Class", default="%sManager" % user_class)

            repo_name = click.prompt("Repository Name", default=project_name.lower().replace(" ", ""))

            artifact_id = click.prompt("Artifact Name", default=project_name.lower().replace(" ", ""))
            plugin_dependencies = click.prompt("Plugin Dependencies", default="Commons")
            spigot_version = click.prompt("Spigot Version", default="1.8.8-R0.1-SNAPSHOT")

            output_dir = click.prompt("Lastly, where do you wish to store the project?",
                                      default=os.path.join(os.path.expanduser("~"), "Projects"))

            # todo implement template selection from menu, and program accordingly!
            if plugin_type == "BukkitPlugin":

                cookiecutter(os.path.join(templates_folder, "/cookiecutter-commons-bukkitplugin/"),
                             output_dir=output_dir, no_input=True,
                             extra_context={
                                 "project_author": project_author,
                                 "project_name": project_name,
                                 "project_version": project_version,
                                 "project_description": project_description,
                                 "main_package": main_package,
                                 "main_class": main_class,
                                 "plugin_type": plugin_type,
                                 "repo_name": repo_name,
                                 "artifact_id": artifact_id,
                                 "plugin_dependencies": plugin_dependencies,
                                 "spigot_version": spigot_version
                             })
            else:

                cookiecutter(os.path.join(templates_folder, "/cookiecutter-commons-minigame/"), output_dir=output_dir,
                             no_input=True,
                             extra_context={
                                 "project_author": project_author,
                                 "project_name": project_name,
                                 "project_version": project_version,
                                 "project_description": project_description,
                                 "main_package": main_package,
                                 "main_class": main_class,
                                 "user_class": user_class,
                                 "user_manager_class": user_manager_class,
                                 "plugin_type": plugin_type,
                                 "repo_name": repo_name,
                                 "artifact_id": artifact_id,
                                 "plugin_dependencies": plugin_dependencies,
                                 "spigot_version": spigot_version
                             })

            project_main_path = os.path.join(output_dir, repo_name, "src", "main", "java")

            project_new_path = os.path.join(output_dir, repo_name)

            project_main_package_path = project_main_path

            if not os.path.exists(project_main_package_path):
                print("PROJECT FAILED TO CREATE. FAILING OUT")
                exit(9)
                return

            project_package_path = main_package.split(".")
            for path in project_package_path:
                project_main_package_path = os.path.join(project_main_package_path, path)

                if not os.path.exists(project_main_package_path):
                    os.mkdir(project_main_package_path)

            if not os.path.exists(project_main_package_path):
                os.makedirs(project_main_package_path)

            main_class_path = os.path.join(project_main_path, "%s.java" % main_class)

            if not os.path.exists(main_class_path):
                print("Unable to locate path %s" % main_class_path)
                return  # todo clean up dir... Shit failed bruh.

            shutil.move(main_class_path, os.path.join(project_main_package_path, "%s.java" % main_class))

            if plugin_type == "MiniGame":

                directory_list = os.listdir(project_main_path)

                for dirname in directory_list:
                    print("Directory %s in MiniGame Template Render" % dirname)
                    shutil.move(os.path.join(project_main_path, dirname), project_main_package_path)
                    print("Moved to %s " % project_main_package_path)

            print("Finished Generating project [%s] @ %s" % (project_name, project_new_path))

            # Get the project configuration directory.
            projects_config_dir = os.path.join(self.config_folder, 'projects')

            # Create the project from prompt.
            project = Project(
                name=project_name,
                directory=project_new_path,
                target_directory=os.path.join(project_new_path, "target"),
                build_command="mvn clean install"
            )

            # Save the project to file!
            # TODO: Move this save operation to the project itself.
            with open(os.path.join(projects_config_dir, '%s.yml' % project.name), 'w') as project_new_config_file:
                yaml.dump(project.yaml(), project_new_config_file, default_flow_style=False)

            print("Created %s.yml file in projects folder to allow management with CraftBuildTools!" % project_name)
            print("Continuing Execution!")

        # If the script was executed with the add-project argument, then we're going
        # to prompt the user for all the options required to create a new project.
        # After the prompting of such, the script will finish execution. Adding projects is
        # an execution that required to be run on its own.
        if self.operations['add_project']:
            # Get the project configuration directory.
            projects_config_dir = os.path.join(self.config_folder, 'projects')

            # Create the project from prompt.
            project = Project.create_from_prompt()

            # Save the project to file!
            # TODO: Move this save operation to the project itself.
            with open(os.path.join(projects_config_dir, '%s.yml' % project.name), 'w') as project_new_config_file:
                yaml.dump(project.yaml(), project_new_config_file, default_flow_style=False)

            print("Created Project!")
            print("================")
            print(project.yaml())
            print("================")

            print("Operations Complete, Adding project to application!")
            self.projects.append(project)

            build_new_project = click.prompt("Append your project to be built?", default=True, type=click.BOOL)

            if build_new_project:
                self.build_projects.append(project.name)

        # Build a todo file!
        if self.operations['todo'] is True:
            # TODo Finish this implementation!
            for project in self.projects:
                todos = {

                }

                if not os.path.exists(project.directory):
                    continue

                print("Scanning %s for Todo Items", project.name)

                files_in_project = project.get_files(match="*.java")
                for project_file in files_in_project:
                    # Todo implement way to have excludes in projects details
                    if ".sync" or ".git" in project_file:
                        continue

                    line_number = 0
                    project_base_file = os.path.basename(project_file)
                    logger.debug("Project Base File: %s", project_base_file)
                    for line in open(project_file):
                        if 'todo' in line.lower():
                            todos[project_base_file] = {
                                os.path.split(project_file)[1]: {
                                    'line-number': line_number,
                                    'text': line.strip()
                                }
                            }

                        line_number += 1

                with open(os.path.join(project.directory, "todo.yml"), 'w') as yaml_file:
                    yaml.dump(todos, yaml_file, default_flow_style=False)
                    # yaml_output = yaml.dump(todos, None, default_flow_style=False)

                print("Created todo.yml in project root %s", project.name)

        # Build all the projects described in the config.yml

        built_projects = []

        if self.operations['build'] is True:
            failed_builds = []
            successful_builds = []
            invalid_project_folders = []

            compile_all = "all" in self.build_projects

            for project in self.projects:
                # If we're not compiling all the projects available
                if not compile_all:
                    # Then check if the projects name is in the projects to build!
                    if project.name not in self.build_projects:
                        continue

                if not os.path.exists(project.directory):
                    invalid_project_folders.append(project.name)
                    continue

                # Change to the working Directory.
                build_status = project.build()

                #         TODO Implement checking for where the build failed
                if build_status is False:
                    logging.error("Failed to build %s using command '%s'", project.name, project.build_command)
                    failed_builds.append(project.name)
                else:
                    successful_builds.append(project.name)
                    built_projects.append(project)

            total_projects = len(self.projects) if compile_all else len(self.build_projects)
            failed_projects = len(failed_builds)
            built_project = total_projects - failed_projects
            print(
                "BUILD OPERATION COMPLETE\nInvalid Projects: %s\nSuccessful Builds: %s\n\tNames: %s\nFailed Builds: %s\n\tNames: %s" %
                (",".join(name for name in invalid_project_folders),
                 built_project,
                 ",".join(name for name in successful_builds),
                 failed_projects,
                 ','.join(name for name in failed_builds)
                 ))

        # Cleans all local files which have been added from previous operations
        if self.operations['clean'] is True:
            for project_jar in self.__get_jar_files():
                print("Removing Jar File %s" % os.path.basename(project_jar))
                os.remove(project_jar)

        # Copy all the files from config locations, to the executing folder.

        copied_files = []

        if self.operations['copy'] is True:
            for project in built_projects:
                pom_info = project.get_pom_info()
                output_jar_path = os.path.join(project.target_directory, pom_info['output_jar'])
                if not os.path.exists(output_jar_path):
                    print("Unable to find %s for project %s" % (pom_info['output_jar'], project.name))
                    continue

                new_file_path = os.path.join(self.files_folder, pom_info['output_jar'])
                shutil.copyfile(output_jar_path, new_file_path)
                copied_files.append(new_file_path)

            print("Copied %s files to %s %s" % (len(copied_files), self.files_folder,
                                                ",".join(project.name for project in self.projects) if len(
                                                    copied_files) > 0 else ""))

        # If there's no files that were copied, we want to upload all the files
        # in the 'files' folder, to the server.
        if len(copied_files) == 0:
            copied_files = self.__get_jar_files()

        if self.operations['upload'] is True:
            if len(copied_files) == 0:
                print("You have no files in your project files folder to upload.")
                return

            ftp_client = ftpretty(host=self.config['ftp-host'], user=self.config['ftp-username'],
                                  password=self.config['ftp-password'])

            put_directory = self.config['remote-upload-directory']

            print("Connected to FTP Remote Host; Uploading files to %s" % put_directory)

            ftp_client.cd(put_directory)

            for copied in copied_files:
                base_file = os.path.basename(copied)
                ftp_client.put(copied, base_file)
                print("Uploaded %s to %s" % (base_file, put_directory))

            ftp_client.close()

        print("Operations complete")


if __name__ == "__main__":
    args = parser.parse_args()
    app = App(args)
    app.run()
