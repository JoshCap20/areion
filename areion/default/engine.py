from jinja2 import Environment, FileSystemLoader
from ..base import BaseEngine


class Engine(BaseEngine):
    """
    Engine class responsible for rendering templates using Jinja2.

    Attributes:
        env (Environment): Jinja2 environment with a file system loader.

    Methods:
        __init__(templates_dir="templates"):
            Initializes the Engine with the specified templates directory.

        render(template_name, context):
            Renders the specified template with the given context.

    Args:
        templates_dir (str): Directory where the templates are stored. Defaults to "templates".

    Methods:
        render(template_name, context):
            Renders the specified template with the given context.

            Args:
                template_name (str): The name of the template to render.
                context (dict): The context to pass to the template.

            Returns:
                str: The rendered template as a string.
    """

    def __init__(self, templates_dir="templates"):
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def render(self, template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)
