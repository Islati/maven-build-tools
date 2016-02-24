from craftbuildtools import OperationPlugin


class CopyOperation(OperationPlugin):
    def __init__(self):
        super(CopyOperation, self).__init__()
        self.name = "copy_operation"
        self.description = "Copy all your brand new, brilliant files to a new location!"

    def perform(self, *args, **kwargs):
        from craftbuildtools import app, logger
        import shutil
        import os
        import click
        from craftbuildtools.utils import get_filename

        copied_files = []

        for project in app.built_projects:
            pom_info = project.get_pom_info()
            output_jar_path = os.path.join(project.target_directory, pom_info['output_jar'])
            if not os.path.exists(output_jar_path):
                click.echo("Unable to find %s for project %s" % (pom_info['output_jar'], project.name))
                continue

            new_file_path = os.path.join(app.files_folder, pom_info['output_jar'])
            shutil.copyfile(output_jar_path, new_file_path)
            copied_files.append(new_file_path)

        click.echo("Copied %s files to %s [%s]" % (
            len(copied_files), app.files_folder, ",".join(get_filename(name) for name in copied_files)
        ))

        app.copied_files = copied_files


copy_operation_plugin = CopyOperation()
