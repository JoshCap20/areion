from jinja2 import Environment, FileSystemLoader
from ..base import BaseEngine


class Engine(BaseEngine):
    def __init__(self, templates_dir="templates"):
        self.env = Environment(loader=FileSystemLoader(templates_dir))

    def render(self, template_name, context):
        template = self.env.get_template(template_name)
        return template.render(context)
