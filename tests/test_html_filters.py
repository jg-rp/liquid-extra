"""Test cases for html filters."""
# pylint: disable=missing-class-docstring,missing-function-docstring

from unittest import skipIf

try:
    import markupsafe  # pylint: disable=unused-import

    MARKUPSAFE_AVAILABLE = True
except ImportError:
    MARKUPSAFE_AVAILABLE = False

from liquid import Environment
from liquid.loaders import DictLoader
from liquid import Markup

from liquid_extra.filters import stylesheet_tag
from liquid_extra.filters import script_tag

from .base import FilterTestCase
from .base import RenderFilterTestCase
from .base import Case
from .base import RenderCase


class StylesheetTagFilterTestCase(FilterTestCase):
    """Test the StylesheetTag template filter."""

    def test_stylesheet_tag_filter(self) -> None:
        test_cases = [
            Case(
                description="relative url",
                val="assets/style.css",
                args=[],
                kwargs={},
                expect=(
                    '<link href="assets/style.css" rel="stylesheet" '
                    'type="text/css" media="all" />'
                ),
            ),
            Case(
                description="remote url",
                val="https://example.com/static/style.css",
                args=[],
                kwargs={},
                expect=(
                    '<link href="https://example.com/static/style.css" '
                    'rel="stylesheet" type="text/css" media="all" />'
                ),
            ),
            Case(
                description="html escape url",
                val="<b>assets/style.css</b>",
                args=[],
                kwargs={},
                expect=(
                    '<link href="&lt;b&gt;assets/style.css&lt;/b&gt;" rel="stylesheet" '
                    'type="text/css" media="all" />'
                ),
            ),
            Case(
                description="not a string",
                val=42,
                args=[],
                kwargs={},
                expect=(
                    '<link href="42" rel="stylesheet" type="text/css" media="all" />'
                ),
            ),
        ]

        self.env.add_filter("stylesheet_tag", stylesheet_tag)
        self._test(self.ctx.filter("stylesheet_tag"), test_cases)


class RenderStylesheetTagFilterTestCase(RenderFilterTestCase):
    """Test the StylesheetTag filter from a template."""

    def test_render_stylesheet_tag_filter(self) -> None:
        test_cases = [
            RenderCase(
                description="from context variable",
                template=r"{{ url | stylesheet_tag }}",
                expect=(
                    '<link href="assets/style.css" rel="stylesheet" '
                    'type="text/css" media="all" />'
                ),
                globals={"url": "assets/style.css"},
                partials={},
            ),
        ]

        for case in test_cases:
            env = Environment()
            env.add_filter("stylesheet_tag", stylesheet_tag)
            env.loader = DictLoader(case.partials)
            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)

    @skipIf(not MARKUPSAFE_AVAILABLE, "this test requires markupsafe")
    def test_render_stylesheet_tag_with_autoescape(self) -> None:
        test_cases = [
            RenderCase(
                description="relative url",
                template=r"{{ url | stylesheet_tag }}",
                expect=(
                    '<link href="assets/style.css" rel="stylesheet" '
                    'type="text/css" media="all" />'
                ),
                globals={"url": "assets/style.css"},
                partials={},
            ),
            RenderCase(
                description="unsafe url from context",
                template=r"{{ url | stylesheet_tag }}",
                expect=(
                    '<link href="&lt;b&gt;assets/style.css&lt;/b&gt;" rel="stylesheet" '
                    'type="text/css" media="all" />'
                ),
                globals={"url": "<b>assets/style.css</b>"},
                partials={},
            ),
            RenderCase(
                description="safe url from context",
                template=r"{{ url | stylesheet_tag }}",
                expect=(
                    '<link href="&lt;b&gt;assets/style.css&lt;/b&gt;" rel="stylesheet" '
                    'type="text/css" media="all" />'
                ),
                globals={"url": Markup("<b>assets/style.css</b>")},
                partials={},
            ),
        ]

        env = Environment(autoescape=True)
        env.add_filter("stylesheet_tag", stylesheet_tag)

        for case in test_cases:
            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)


class ScriptTagFilterTestCase(FilterTestCase):
    """Test the ScriptTag template filter."""

    def test_script_tag_filter(self) -> None:
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
                expect=(
                    "<script "
                    'src="https://example.com/static/assets/app.js" '
                    'type="text/javascript">'
                    "</script>"
                ),
            ),
            Case(
                description="not a string",
                val=42,
                args=[],
                kwargs={},
                expect='<script src="42" type="text/javascript"></script>',
            ),
        ]

        self.env.add_filter("script_tag", script_tag)
        self._test(self.ctx.filter("script_tag"), test_cases)


class RenderScriptTagFilterTestCase(RenderFilterTestCase):
    """Test the ScriptTag filter from a template."""

    def test_render_script_tag_filter(self) -> None:
        test_cases = [
            RenderCase(
                description="url from context",
                template=r"{{ url | script_tag }}",
                expect=(
                    '<script src="assets/assets/app.js" '
                    'type="text/javascript"></script>'
                ),
                globals={"url": "assets/assets/app.js"},
                partials={},
            ),
        ]

        # Test new style filter implementation
        for case in test_cases:
            env = Environment()
            env.add_filter("script_tag", script_tag)
            env.loader = DictLoader(case.partials)
            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)

    @skipIf(not MARKUPSAFE_AVAILABLE, "this test requires markupsafe")
    def test_render_script_tag_with_autoescape(self) -> None:
        test_cases = [
            RenderCase(
                description="relative url",
                template=r"{{ url | script_tag }}",
                expect=(
                    '<script src="assets/assets/app.js" '
                    'type="text/javascript"></script>'
                ),
                globals={"url": "assets/assets/app.js"},
                partials={},
            ),
            RenderCase(
                description="unsafe url from context",
                template=r"{{ url | script_tag }}",
                expect=(
                    '<script src="&lt;b&gt;assets/assets/app.js&lt;/b&gt;" '
                    'type="text/javascript"></script>'
                ),
                globals={"url": "<b>assets/assets/app.js</b>"},
                partials={},
            ),
            RenderCase(
                description="safe url from context",
                template=r"{{ url | script_tag }}",
                expect=(
                    '<script src="&lt;b&gt;assets/assets/app.js&lt;/b&gt;" '
                    'type="text/javascript"></script>'
                ),
                globals={"url": Markup("<b>assets/assets/app.js</b>")},
                partials={},
            ),
        ]

        env = Environment(autoescape=True)
        env.add_filter("script_tag", script_tag)

        for case in test_cases:
            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)
