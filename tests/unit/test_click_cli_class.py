import click

CONTEXT_SETTINGS = dict(
    auto_envvar_prefix='COMPLEX'
)


class AppContext(object):
    def __init__(self):
        self.name = "Brandon"
        self.greeting = "Hello, "
        self.after_greet = "FROM THE OTHER SIIIIIIIIIIDE"


pass_context = click.make_pass_decorator(AppContext, True)


@click.command("hello")
@pass_context
def perform_hello(ctx):
    print("%s%s" % (ctx.greeting, ctx.name))


@click.command("otherside")
@pass_context
def perform_otherside(ctx):
    print("%s" % ctx.after_greet)


class Commands(object):
    def __init__(self):
        self.commands = {
            'perform_hello': perform_hello,
            'perform_otherside': perform_otherside
        }


commands = Commands()


class ClickCLITest(click.MultiCommand):
    def __init__(self, **kwargs):
        super(ClickCLITest, self).__init__(**kwargs)
        self.chain = True
        self.no_args_is_help = True

    def get_command(self, ctx, cmd_name):
        name = "perform_%s" % cmd_name
        if name not in commands.commands:
            return
        return commands.commands[name]

    def list_commands(self, ctx):
        cmds = []

        for cmd, delegate in commands.commands:
            if cmd.startswith("perform_"):
                cmds.append(cmd.replace("perform_", ""))

        cmds.sort()
        return cmds


@click.command(cls=ClickCLITest, context_settings=CONTEXT_SETTINGS)
@pass_context
def run_app(ctx):
    print("Beginning App Execution")


if __name__ == "__main__":
    run_app()
