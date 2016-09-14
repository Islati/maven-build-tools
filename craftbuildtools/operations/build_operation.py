import logging
import os
import subprocess
from craftbuildtools.operations import OperationPlugin
from craftbuildtools.utils import ChangeDir

logger = logging.getLogger("craft-buildtools")


class MavenBuildOperation(OperationPlugin):
    def __init__(self):
        super(MavenBuildOperation, self).__init__()
        self.name = "build_operation"
        self.description = "Mange your projects and generate builds (Maven Only)"

    def perform(self, *args, **kwargs):
        import click

        failed_builds = []
        successful_builds = []
        invalid_project_folders = []
        total_project_count = 0

        build_projects = kwargs.pop('build_projects')
        build_projects.sort()

        projects = kwargs.pop('projects')

        if (build_projects is None or len(build_projects) is 0) or (projects is None or len(projects) is 0):
            click.echo("There are no projects to be built")
            return

        from threading import Thread

        def call_maven_build(bp):
            with ChangeDir(bp.directory):
                click.echo("Executing build command '%s' on Project %s" % (bp.build_command, bp.name))

                # TODO Implement timer to see how long build starts, or spawn in a subprocess.
                build_process = subprocess.Popen(bp.build_command, shell=True, stdout=subprocess.PIPE,
                                                 stderr=subprocess.STDOUT)
                logger.debug("Build process has been spawned %s" % build_process.pid)

                build_success = False
                for line in build_process.stdout.readlines():
                    if b"BUILD SUCCESS" in line:
                        logger.debug("Maven Build Success in line: '%s'" % line)
                        build_success = True
                        break

                build_process.wait()

                if build_success is True:
                    click.echo("Project %s has been built successfully" % bp.name)
                    successful_builds.append(bp.name)
                else:
                    click.echo("Project %s has failed to build" % bp.name)
                    failed_builds.append(bp.name)

        if build_projects is None or len(build_projects) == 0:
            click.echo("There were no projects specified to be built")
            return None, None

        for project_name in build_projects:
            total_project_count += 1
            project = projects[project_name]

            if not os.path.exists(project.directory):
                invalid_project_folders.append(project.name)
                click.echo("Project %s folder (%s) doesn't exist... Is it valid?" % (project.name, project.directory))
                continue

            build_thread = Thread(target=call_maven_build, args=(project,))
            build_thread.start()
            logger.debug("Thread to build %s has been executed" % project.name)
            build_thread.join()
            logger.debug("Build Thread for %s has expired" % project.name)

        failed_projects = len(failed_builds)
        built_project = total_project_count - failed_projects - len(invalid_project_folders)
        click.echo(
            "BUILD OPERATION COMPLETE\nInvalid Projects: %s\nSuccessful Builds: %s\n\tNames: %s\nFailed Builds: %s\n\tNames: %s" %
            (",".join(name for name in invalid_project_folders),
             built_project,
             ",".join(name for name in successful_builds),
             failed_projects,
             ','.join(name for name in failed_builds)
             ))

        return successful_builds, failed_builds


build_plugin = MavenBuildOperation()
