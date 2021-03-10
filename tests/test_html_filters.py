from liquid_extra.filters import StylesheetTag
from liquid_extra.filters import ScriptTag

from liquid.exceptions import FilterArgumentError

from .base import FilterTestCase
from .base import RenderFilterTestCase
from .base import Case
from .base import RenderCase


class StylesheetTagFilterTestCase(FilterTestCase):
    """Test the StylesheetTag template filter."""

    def test_StylesheetTag_filter(self):
        test_cases = [
            Case(
                description="relative url",
                val="assets/style.css",
                args=[],
                kwargs={},
                expect='<link href="assets/style.css" rel="stylesheet" type="text/css" media="all" />',
            ),
            Case(
                description="remote url",
                val="https://example.com/static/style.css",
                args=[],
                kwargs={},
                expect='<link href="https://example.com/static/style.css" rel="stylesheet" type="text/css" media="all" />',
            ),
            Case(
                description="not a string",
                val=42,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self.env.add_filter(StylesheetTag.name, StylesheetTag(self.env))
        self._test(self.ctx.filter(StylesheetTag.name), test_cases)


class RenderStylesheetTagFilterTestCase(RenderFilterTestCase):
    """Test the StylesheetTag filter from a template."""

    def test_render_StylesheetTag_filter(self):
        test_cases = [
            RenderCase(
                description="array of strings",
                template=r"{{ url | stylesheet_tag }}",
                expect='<link href="assets/style.css" rel="stylesheet" type="text/css" media="all" />',
                globals={"url": "assets/style.css"},
                partials={},
            ),
        ]

        self._test(StylesheetTag(self.env), test_cases)


class ScriptTagFilterTestCase(FilterTestCase):
    """Test the ScriptTag template filter."""

    def test_ScriptTag_filter(self):
        test_cases = [
            Case(
                description="relative url",
                val="assets/app.js",
                args=[],
                kwargs={},
                expect='<script src="assets/app.js" type="text/javascript"></script>',
            ),
            Case(
                description="remote url",
                val="https://example.com/static/assets/app.js",
                args=[],
                kwargs={},
                expect='<script src="https://example.com/static/assets/app.js" type="text/javascript"></script>',
            ),
            Case(
                description="not a string",
                val=42,
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self.env.add_filter(ScriptTag.name, ScriptTag(self.env))
        self._test(self.ctx.filter(ScriptTag.name), test_cases)


class RenderScriptTagFilterTestCase(RenderFilterTestCase):
    """Test the ScriptTag filter from a template."""

    def test_render_ScriptTag_filter(self):
        test_cases = [
            RenderCase(
                description="array of strings",
                template=r"{{ url | script_tag }}",
                expect='<script src="assets/assets/app.js" type="text/javascript"></script>',
                globals={"url": "assets/assets/app.js"},
                partials={},
            ),
        ]

        self._test(ScriptTag(self.env), test_cases)
