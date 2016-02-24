import os
from bs4 import BeautifulSoup
import click
import yaml
from craftbuildtools.utils import get_files_recursive
import craftbuildtools as cbt


class Project(object):
    def __init__(self, name, directory, target_directory, build_command="mvn clean install"):
        self.name = name
        self.directory = os.path.expanduser(directory)
        self.target_directory = os.path.expanduser(target_directory)
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
        click.echo("Please enter your project information!")
        name = click.prompt("Project Name")
        directory = click.prompt("Project Directory")
        target_directory = click.prompt("Project Build Directory", default=os.path.join(directory, "target"))

        build_command = click.prompt("Project Build Command", default="mvn clean install")
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
            cbt.logger.warn("Project %s has no pom.xml at expects '%s'" % (self.name, pom_path))
            return None

        return pom_path

    def __has_pom_file(self):
        return self.__get_pom_file() is not None

    def get_pom_info(self):
        pom_file = self.__get_pom_file()
        if pom_file is None:
            cbt.logger.warn("Unable to find pom file for project %s" % self.name)
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
