import fnmatch
import yaml
import os
import shutil
import argparse
import subprocess
import logging

from logging.config import dictConfig
from builtins import input
from bs4 import BeautifulSoup

# TODo Eventually make it able to scan for projects based on where they're stored!
# TODO Implement FTP output to server with directory

parser = argparse.ArgumentParser(description="Options to run CraftBuildTools By")
parser.add_argument('--copy', action="store_true", help="Copy Files Flag")
parser.add_argument('--clean', action='store_true', help='Clear all files currently here before copying')
parser.add_argument('--config', required=False, type=argparse.FileType)
parser.add_argument('--addfile', required=False, nargs='*',
                    help="Files which to add to the config.yml file, for performing operations on")
parser.add_argument('--build', required=False, action="store_true")
# TODO Create an argument group for adding projects, with sub args dependant on how its structured
parser.add_argument('--addproject', action="store_true", required=False,
                    help='Directories of Maven projects which to add!')
parser.add_argument('--todo', required=False, action="store_true", help="Flag used to generate the todo file")

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
        'file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'log_format',
            'filename': 'builds.log',
            # os.path.join(os.path.dirname(os.path.realpath(__file__)), "/logs/","%s.log" % time.strftime("%H-%M-%S")),
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

            build_value = build_process.wait()

            build_success = any("BUILD SUCCESS" in line for line in maven_build_lines)
            if build_success is True:
                print("Project %s has been built successfully" % self.name)
            else:
                print("Project %s has failed to build" % self.name)
        return build_success


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

        # Todo Move operations to classes that are executed with args.
        self.operations = {
            'copy': args.copy,
            'clean': args.clean,
            'build': args.build,
            'todo': args.todo,
            'add_project': args.addproject
        }

        # Check if there's any files to add
        if args.addfile:
            self.operations['add_copy_file'] = [file for file in args.add]
        else:
            self.operations['add_copy_file'] = []

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
                # TODO Implement directory searching / matching based on input.
                # TODO Implement copy files into each project.
                'copy_files': [
                    '/home/brandon/Projects/Commons/target/commons-1.8.8.jar',
                    '/home/brandon/Dropbox/Raiders/Core/out/Raiders.jar',
                ]
            }

        with open(self.config_location, 'w') as yaml_file:
            yaml.dump(self.config, yaml_file, default_flow_style=False)

        print("Configuration for CraftBuildTools has been saved at %s", self.config_location)

    def __load_config(self):
        with open(self.config_location, 'r') as yaml_file:
            self.config = yaml.load(yaml_file)

    def run(self):
        dest_loc = self.__executing_location()

        # If the script was executed with the add-project argument, then we're going
        # to prompt the user for all the options required to create a new project.
        # After the prompting of such, the script will finish execution. Adding projects is
        # an execution that required to be run on its own.
        if self.operations['add_project']:
            # Get the project configuration directory.
            projects_config_dir = os.path.join(self.__executing_location(), 'projects')

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
            return

        # Build a todo file!
        if self.operations['todo'] is True:
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
        if self.operations['build'] is True:
            failed_builds = []
            successful_builds = []
            for project in self.projects:
                if not os.path.exists(project.directory):
                    continue

                # Change to the working Directory.
                build_status = project.build()
                #         TODO Implement checking for where the build failed
                if build_status is False:
                    logging.error("Failed to build %s using command '%s'", project.name, project.build_command)
                    failed_builds.append(project.name)
                else:
                    successful_builds.append(project.name)

            total_projects = len(self.projects)
            failed_projects = len(failed_builds)
            built_project = total_projects - failed_projects
            print("BUILD OPERATION COMPLETE\nSuccessful Builds: %s\n\tNames: %s\nFailed Builds: %s\n\tNames: %s" %
                  (built_project,
                   ",".join(name for name in successful_builds),
                   failed_projects,
                   ','.join(name for name in failed_builds)
                   ))

        # Cleans all local files which have been added from previous operations
        if self.operations['clean'] is True:
            # TODO Implement caching for files that have been added to output directory.
            # Clean all the local files that have been copied in via projects.
            for project in self.projects:
                local_path = os.path.join(self.__executing_location(),
                                          os.path.basename(project.get_pom_info()['output_jar']))
                if not os.path.exists(local_path):
                    continue

                os.remove(local_path)

        # Copy all the files from config locations, to the executing folder.
        if self.operations['copy'] is True:
            for project in self.projects:
                output_jar_path = os.path.join(project.target_directory, project.get_pom_info()['output_jar'])
                print("Output Jar Path for %s is %s" % (project.name, output_jar_path))
                if not os.path.exists(output_jar_path):
                    print("Unable to find %s for project %s" % (project.get_pom_info()['output_jar'], project.name))
                    continue

                shutil.copyfile(output_jar_path, os.path.join(dest_loc, project.get_pom_info()['output_jar']))

        print("Operations complete")


if __name__ == "__main__":
    args = parser.parse_args()
    app = App(args)
    app.run()
