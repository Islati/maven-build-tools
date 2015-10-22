import fnmatch
import yaml
import os
import shutil
import argparse
import subprocess
import logging
from logging.config import dictConfig
from logging import FileHandler

# TODo Eventually make it able to scan for projects based on where they're stored!

parser = argparse.ArgumentParser(description="Options to run CraftBuildTools By")
parser.add_argument('--copy', action="store_true", help="Copy Files Flag")
parser.add_argument('--clean', action='store_true', help='Clear all files currently here before copying')
parser.add_argument('--config', required=False, type=argparse.FileType)
parser.add_argument('--addfile', required=False, nargs='*',
                    help="Files which to add to the config.yml file, for performing operations on")
parser.add_argument('--build', required=False, action="store_true")
# TODO Create an argument group for adding projects, with sub args dependant on how its structured
parser.add_argument('--addproject', required=False, nargs='*', help='Directories of Maven projects which to add!')
parser.add_argument('--todo', required=False, action="store_true", help="Flag used to generate the todo file")

# TODO Make some implementation of the mary jane.

# TODO Implement option to run tools.py --build [project-name] --copy [Name [Name]]

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
        'file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'log_format',
            'filename': os.path.join(os.path.dirname(os.path.realpath(__file__))),
            'level': logging.DEBUG
        }
    },
    loggers={
        'root': {
            'handlers': ['stream_handler', 'file_handler'],
            'level': logging.DEBUG
        }
    }
)

dictConfig(logging_config)

logger = logging.getLogger()


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
        return yaml.dump(self.__dict__)

    @staticmethod
    def load(data):
        values = yaml.safe_load(data)
        return Project(
            name=values['name'],
            directory=values['directory'],
            target_directory=values['target_directory'],
            build_command=values['build_command']
        )

    def get_files(self, match="*.*"):
        return get_files_recursive(self.directory, match=match)

    def build(self):

        with ChangeDir(self.directory):

            logger.info("Starting maven build build on directory %s" % project)

            # TODO Implement timer to see how long build starts, or spawn in a subprocess.

            build_process = subprocess.Popen('mvn clean install', shell=True, stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT)

            maven_build_lines = []
            for line in build_process.stdout.readlines():
                maven_build_lines.append(line)

            build_value = build_process.wait()

            if any("BUILD SUCCESS" in line for line in maven_build_lines):
                print("[BUILD] Project '%s' has been built successfully!" % project)
            else:
                print("[BUILD] Project '%s' has failed to build!" % project)

                # todo implement log file for all actions completed


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

        self.operations = {
            'copy': args.copy,
            'clean': args.clean,
            'build': args.build,
            'todo': args.todo
        }

        # Check if there's any files to add
        if args.addfile:
            self.operations['add_copy_file'] = [file for file in args.add]
        else:
            self.operations['add_copy_file'] = []

        # TODO Move this to creation of project object!
        if args.addproject:
            self.operations['add_project'] = [project for project in args.addproject]
        else:
            self.operations['add_project'] = []

        if args.config:
            self.config_location = args.config
        else:
            self.config_location = os.path.join(self.__executing_location(), "config.yml")

        self.__init_config()

        self.__load_projects()

    def __executing_location(self):
        return os.path.dirname(os.path.realpath(__file__))

    def __load_projects(self):
        projects_config_dir = os.path.join(self.__executing_location(), 'projects')
        project_config_files = get_files_recursive(projects_config_dir, '.yml')

        # There's no project files to load, so let's make a dummy file and save it.
        if len(project_config_files) == 0:
            self.projects.append(
                # Add Commons as a default project
                Project(
                    name="Commons",
                    directory="/home/brandon/Projects/Commons/",
                    target_directory="/home/brandon/Projects/Commons/target/",
                    build_command="mvn clean install"
                )
            )

            for project in self.projects:
                with open(os.path.join(projects_config_dir, '%s.yml' % project.name), 'w') as project_new_config_file:
                    yaml.dump(project.yaml(), project_new_config_file, default_flow_style=False)

                logger.debug("Created Project File %s.yml;\r\n Data[\r\n%s\r\n]", project.name, project.yaml())

        for project_config_file in project_config_files:
            project = None
            with open(project_config_file, 'r') as project_file:
                project = yaml.load(project_file)
                self.projects.append(project)
                # print("[INFO] Loaded Project '%s' from File" % project.name)

        logger.info("Loaded Projects [%s] from config folder.", ",".join(project.name for project in self.projects))

    def __init_config(self):
        if not os.path.isfile(self.config_location):
            self.__create_config()

        self.__load_config()

    def __create_config(self):
        if not self.config:
            self.config = {
                # TODO Implement directory searching / matching based on input.
                'copy_files': [
                    '/home/brandon/Projects/Commons/target/commons-1.8.8.jar',
                    '/home/brandon/Dropbox/Raiders/Core/out/Raiders.jar',
                ]
            }

        with open(self.config_location, 'w') as yaml_file:
            yaml.dump(self.config, yaml_file, default_flow_style=False)

        logger.info("Configuration for CraftBuildTools has been saved at %s", self.config_location)

    def __load_config(self):
        with open(self.config_location, 'r') as yaml_file:
            self.config = yaml.load(yaml_file)

    def run(self):
        files_to_copy = self.config['copy_files']

        dest_loc = self.__executing_location()

        # ADDING FILES OPERATION! SAVES NEW FILE LOCATIONS TO CONFIG
        if len(self.operations['add_copy_file']) > 0:
            for file in self.operations['add_copy_file']:
                if not os.path.isfile(file):
                    continue
                path = os.path.realpath(file)
                files_to_copy.append(path)

            self.config['copy_files'] = files_to_copy
            # Will save config to file!
            self.__create_config()

        # Add a project to the list of projects stored in config.yml
        if len(self.operations['add_project']) > 0:
            pass
            # for project in projects:
            #     if not os.path.exists(project):
            #         # Unable to find project at the given folder.
            #         continue
            #
            #     # Add the project to the list of projects!
            #     projects.append(project)
            #     print("[INFO] Added project '%s' to list of projects for build!" % project)
            #
            # self.config['projects'] = projects
            # self.__create_config()
            # print("Configuration has been saved!")

        # Build a todo file!
        if self.operations['todo'] is True:
            for project in self.projects:
                todos = {

                }

                if not os.path.exists(project.directory):
                    continue

                logging.info("Scanning %s for Todo Items", project.name)

                files_in_project = project.get_files(match="*.java")
                for project_file in files_in_project:
                    # Todo implement way to have excludes in project details
                    if ".sync" in project_file:
                        continue

                    line_number = 0
                    project_base_file = os.path.basename(project_file)
                    logger.debug("Project Base File: %s",project_base_file)
                    for line in open(project_file):
                        if 'todo' in line.lower():
                            # print(
                            #     "TODO found at line[%s] in file[%s] saying \"%s\"" % (line_number, project_file, line))
                            todos[project_base_file] = {
                                os.path.split(project_file)[1]: {
                                    'line-number': line_number,
                                    'text': line.strip()
                                }

                            }
                        line_number += 1

                with open(self.config_location, 'w') as yaml_file:
                    yaml.dump(todos, yaml_file, default_flow_style=False)
                    # yaml_output = yaml.dump(todos, None, default_flow_style=False)

        # Build all the projects described in the config.yml
        if self.operations['build'] is True:
            for project in self.projects:
                if not os.path.exists(project.directory):
                    continue

                # Change to the working Directory.
                build_status = project.build()

        # Cleans all local files which have been added from previous operations
        if self.operations['clean'] is True:
            for file in files_to_copy:
                local_path = os.path.join(self.__executing_location(), os.path.basename(file))
                if not os.path.exists(local_path):
                    continue

                os.remove(file)

        # Copy all the files from config locations, to the executing folder.
        if self.operations['copy'] is True:
            for file in files_to_copy:
                if not os.path.exists(file):
                    # TODO Implement removal of files from operation yml file / Comment it out at a line or something.
                    print("[INFO] File '%s' does not exist." % file)
                    continue

                shutil.copy(file, dest_loc)

        print("Operations complete")


if __name__ == "__main__":
    args = parser.parse_args()

    app = App(args)
    app.run()
