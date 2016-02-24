import os
from ftpretty import ftpretty
from craftbuildtools import OperationPlugin


class UploadOperation(OperationPlugin):
    def __init__(self):
        super(UploadOperation, self).__init__()
        self.name = "upload_operation"
        self.description = "Upload the files compiled or copied to a remote server!"

    def perform(self, *args, **kwargs):
        from craftbuildtools import app, logger
        import click

        files_to_copy = app.copied_files
        if len(files_to_copy) == 0:
            files_to_copy = app.get_jar_files()

        ftp_client = ftpretty(host=kwargs.pop("host"), user=kwargs.pop("user"),
                              password=kwargs.pop("password"))

        put_directory = kwargs.pop('directory')

        click.echo("Connected to FTP Remote Host; Uploading files to %s" % put_directory)

        ftp_client.cd(put_directory)

        for copied in files_to_copy:
            base_file = os.path.basename(copied)
            ftp_client.put(copied, base_file)
            click.echo("Uploaded %s to %s" % (base_file, put_directory))

        ftp_client.close()


upload_operation = UploadOperation()
