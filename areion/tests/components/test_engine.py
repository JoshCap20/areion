import unittest
from unittest.mock import patch, Mock
from areion.default import Engine

class TestEngine(unittest.TestCase):

    def setUp(self):
        self.engine = Engine(templates_dir="templates")

    @patch('jinja2.Environment.get_template')
    def test_template_render(self, mock_get_template):
        mock_template = Mock()
        mock_get_template.return_value = mock_template
        mock_template.render.return_value = "Rendered HTML"

        rendered = self.engine.render("test.html", {"title": "Hello"})
        self.assertEqual(rendered, "Rendered HTML")