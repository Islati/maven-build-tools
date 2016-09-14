import logging

from craftbuildtools.operations import OperationPlugin

logger = logging.getLogger("craft-buildtools")


class CopyOperation(OperationPlugin):
    def __init__(self):
        super(CopyOperation, self).__init__()
        self.name = "copy_operation"
        self.description = "Copy all your brand new, brilliant files to a new location!"

    def perform(self, *args, **kwargs):
        import shutil
        import os
        import click
        from craftbuildtools.utils import get_filename

        built_projects = kwargs.pop('built_projects')
        files_folder = kwargs.pop('files_folder')

        copied_files = []

        for project in built_projects:
            pom_info = project.get_pom_info()
            output_jar_path = os.path.join(project.target_directory, pom_info['output_jar'])
            if not os.path.exists(output_jar_path):
                click.echo("Unable to find %s for project %s" % (pom_info['output_jar'], project.name))
                continue

            new_file_path = os.path.join(files_folder, pom_info['output_jar'])
            shutil.copyfile(output_jar_path, new_file_path)
            copied_files.append(new_file_path)

        click.echo("Copied %s files to %s [%s]" % (
            len(copied_files), files_folder, ",".join(get_filename(name) for name in copied_files)
        ))

        return copied_files


copy_operation_plugin = CopyOperation()
