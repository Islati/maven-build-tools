from simpleplugins import Plugin


class TemplateRenderPlugin(Plugin):
    def __init__(self, **kwargs):
        super(TemplateRenderPlugin, self).__init__(**kwargs)
        self.template_name = kwargs.pop("template_name")

    def deactivate(self):
        self.active = False

    def perform(self, **kwargs):
        raise NotImplementedError("Unable to render template; Method to handle rendering is not implemented.")

    def activate(self):
        self.active = True
