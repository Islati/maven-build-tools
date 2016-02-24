import inspect
import os
import click
from craftbuildtools import OperationPlugin
from craftbuildtools.template import TemplateRenderPlugin


class CreateProjectOperation(OperationPlugin):
    def __init__(self):
        super(CreateProjectOperation, self).__init__()
        self.name = "createproject_operation"
        self.description = "Generate a project for you to hack on via a CookieCutter Template"

    def perform(self, *args, **kwargs):
        from craftbuildtools import app, logger
        from craftbuildtools.utils import ChangeDir, get_filename

        templates_folder = kwargs.pop("templatefolder")
        template = kwargs.pop("template")
        git_repo = kwargs.pop("git_clone_repo")

        if not os.path.exists(templates_folder):
            os.makedirs(templates_folder)

        new_git_repo = click.prompt("Would you like to add a new template?", default=False, type=click.BOOL)

        if new_git_repo:
            git_repo = click.prompt("Enter the URL For your git-repo to use as a template", type=click.STRING)

        # If there was a git repository included in the arguments, then
        # Attempt to clone this done!
        if git_repo is not None:
            # Enter the Templates Folder!
            with ChangeDir(templates_folder):
                # Get the name of the folder, from the git repo.
                cloned_folder_name = get_filename(git_repo)
                # If the git repository doesn't exist then we need to clone it doen.
                if not os.path.exists(os.path.join(templates_folder, cloned_folder_name)):
                    git.clone(git_repo)

                    if not os.path.exists(os.path.join(templates_folder, cloned_folder_name).replace(".git", "")):
                        logger.error("Unable to find cloned repo %s at expected location %s" % (
                            cloned_folder_name, os.path.join(templates_folder, cloned_folder_name)))
                        exit()
                        return
                else:
                    click.echo("Git Repo %s already exists at %s" % (cloned_folder_name, templates_folder))

        available_templates = []

        for file in os.listdir(templates_folder):
            file = os.path.join(templates_folder, file)
            logger.debug("First Loop File: %s" % file)
            if os.path.isdir(file):
                logger.debug("%s is dir" % file)
                available_templates.append(file)

        # If there's no template or git_repo available, and no projects
        # In the available templates folder.
        if len(available_templates) == 0:
            click.echo("A template is required in order to create a project.")
            wants_to_clone = click.prompt("Would you like to clone a git repo for your template?", default=True,
                                          type=click.BOOL)

            try:
                from sh import git
            except:
                click.echo(
                    "You must have git installed on your machine in order to perform a clone. Aborting. Install git and try again")

                exit()
                return

            if not wants_to_clone:
                clone_commons_templates = click.prompt("Would you like to clone the default repositories?",
                                                       default=True, type=click.BOOL)

                if not clone_commons_templates:
                    logger.error("You must have atleast one available template in-order to create a project")
                    exit()
                    return

                with ChangeDir(templates_folder):
                    # TODO Read list of default repositories from config on git. Or something.

                    cloned = 0

                    if not os.path.exists(os.path.join(templates_folder, "cookiecutter-commons-bukkitplugin")):
                        logger.info("Cloning CookieCutter Template: Commons (BukkitPlugin)")
                        git.clone('https://github.com/TechnicalBro/cookiecutter-commons-bukkitplugin.git')
                        cloned += 1

                    if not os.path.exists(os.path.join(templates_folder, "cookiecutter-commons-minigame")):
                        logger.info("Cloning CookieCutter Template: Commons (MiniGame)")
                        git.clone("https://github.com/TechnicalBro/cookiecutter-commons-minigame.git")
                        cloned += 1

                    if not os.path.exists(os.path.join(templates_folder, "cookiecutter-bukkit-maven")):
                        logger.info("Cloning CookieCutter Template: Bukkit Plugin")
                        git.clone("https://github.com/TechnicalBro/cookiecutter-bukkit-maven.git")
                        cloned += 1

                    if cloned > 0:
                        logger.info("Finished Cloning available repositories.")

            else:
                git_repo = click.prompt("Enter the URL of the git repo to clone", type=click.STRING)

                with ChangeDir(templates_folder):
                    # Get the name of the folder, from the git repo.
                    cloned_folder_name = get_filename(git_repo)
                    # If the git repository doesn't exist then we need to clone it doen.
                    if not os.path.exists(os.path.join(templates_folder, cloned_folder_name)):
                        git.clone(git_repo)

                        if not os.path.exists(os.path.join(templates_folder, cloned_folder_name).replace(".git", "")):
                            logger.error("Unable to find cloned repo %s at expected location %s" % (
                                cloned_folder_name, os.path.join(templates_folder, cloned_folder_name)))
                            exit()
                            return
                    else:
                        click.echo("Git Repo %s already exists at %s" % (cloned_folder_name, templates_folder))

        available_templates = []

        logger.debug("Templates Folder is %s" % templates_folder)

        for file in os.listdir(templates_folder):
            file = os.path.join(templates_folder, file)

            if os.path.isdir(file):
                available_templates.append(file)
                logger.debug("Available Template: %s" % file)
            else:
                logger.debug("%s is not a directory" % file)

        if len(available_templates) == 0:
            click.echo("There's no available templates to choose from. Exiting")
            exit()

        templates_data = {}

        app.plugin_manager.register(directory=templates_folder, skip_types=OperationPlugin, override=True)

        if not app.plugin_manager.has_plugin(plugin_type=TemplateRenderPlugin):
            logger.error(
                "Unable to locate template rendering plugins in Plugin Manager. Assure your template has a script to render it by.")
            exit()
            return

        template_plugins = app.plugin_manager.get_plugins(plugin_type=TemplateRenderPlugin)
        for plugin in template_plugins:
            templates_data[plugin.template_name] = {
                'plugin': plugin,
                'folder': os.path.dirname(inspect.getfile(plugin.__class__))
            }

        logger.debug("Template Data map is: %s" % str(templates_data))

        project_type = template
        if project_type not in template_plugins:
            project_type_prompt_text = "Which Template Would you like to Render? Choose from ({})".format(
                ', '.join(templates_data.keys()))

            project_type = click.prompt(project_type_prompt_text, type=click.Choice(templates_data.keys()))

        template_plugin = templates_data[project_type]['plugin']
        template_plugin.perform(directory=templates_data[project_type]['folder'])


create_project_operation_plugin = CreateProjectOperation()
