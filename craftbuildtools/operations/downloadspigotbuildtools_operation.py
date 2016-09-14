import logging
import os
import requests
from craftbuildtools.operations import OperationPlugin

logger = logging.getLogger("craft-buildtools")


class DownloadSpigotBuildToolsOperation(OperationPlugin):
    spigot_build_tools_url = "https://hub.spigotmc.org/jenkins/job/BuildTools/lastSuccessfulBuild/artifact/target/BuildTools.jar"

    def __init__(self):
        super(DownloadSpigotBuildToolsOperation, self).__init__()

        self.name = "download_buildtools"
        self.description = "Download the latest version of spigot's BuildTools.jar to retrieve the latest server jar files."

    def perform(self, *args, **kwargs):
        save_location = kwargs.get("save_location", default=os.getcwd())

        if os.path.isdir(save_location):
            save_location = os.path.join(os.path.expanduser(save_location), "BuildTools.jar")

        with open(save_location, 'wb') as handle:
            response = requests.get(self.spigot_build_tools_url, stream=True)

            if not response.ok:
                logger.error("Error when downloading BuildTools")
                return

            for block in response.iter_content(1024):
                handle.write(block)

            if os.path.exists(save_location):
                logger.info("Successfully downloaded BuildTools.jar")
            else:
                logger.error("BuildTools.jar Failed To Download")

download_tools_operation = DownloadSpigotBuildToolsOperation()