"""Test `with` tag parsing and rendering."""
# pylint: disable=missing-class-docstring

from dataclasses import dataclass
from dataclasses import field

from typing import Dict

from unittest import TestCase

from liquid import Environment
from liquid.template import Refs

from liquid_extra.tags import WithTag


@dataclass
class Case:
    """Table driven test helper."""

    description: str
    template: str
    expect: str
    globals: Dict[str, object] = field(default_factory=dict)


class RenderWithTagTestCase(TestCase):
    def test_render_with_tag(self) -> None:
        """Test that we can render a `with` tag."""
        test_cases = [
            Case(
                description="block scoped variable",
                template=r"{{ x }}{% with x: 'foo' %}{{ x }}{% endwith %}{{ x }}",
                expect="foo",
            ),
            Case(
                description="block scoped alias",
                template=(
                    r"{% with p: collection.products.first %}"
                    r"{{ p.title }}"
                    r"{% endwith %}"
                    r"{{ p.title }}"
                    r"{{ collection.products.first.title }}"
                ),
                expect="A ShoeA Shoe",
                globals={"collection": {"products": [{"title": "A Shoe"}]}},
            ),
            Case(
                description="multiple block scoped variables",
                template=(
                    r"{% with a: 1, b: 3.4 %}"
                    r"{{ a }} + {{ b }} = {{ a | plus: b }}"
                    r"{% endwith %}"
                ),
                expect="1 + 3.4 = 4.4",
            ),
        ]

        env = Environment()
        env.add_tag(WithTag)

        for case in test_cases:
            with self.subTest(msg=case.description):
                template = env.from_string(case.template, globals=case.globals)
                self.assertEqual(template.render(), case.expect)


class AnalyzeWithTestCase(TestCase):
    def test_analyze_macro_tag(self) -> None:
        """Test that we can statically analyze macro and call tags."""
        env = Environment()
        env.add_tag(WithTag)

        template = env.from_string(
            r"{% with p: collection.products.first %}"
            r"{{ p.title }}"
            r"{% endwith %}"
            r"{{ p.title }}"
            r"{{ collection.products.first.title }}"
        )

        expected_template_globals = {
            "collection.products.first": [("<string>", 1)],
            "p.title": [("<string>", 1)],
            "collection.products.first.title": [("<string>", 1)],
        }
        expected_template_locals: Refs = {}
        expected_refs = {
            "collection.products.first": [("<string>", 1)],
            "collection.products.first.title": [("<string>", 1)],
            "p.title": [("<string>", 1), ("<string>", 1)],
        }

        analysis = template.analyze()

        self.assertEqual(analysis.local_variables, expected_template_locals)
        self.assertEqual(analysis.global_variables, expected_template_globals)
        self.assertEqual(analysis.variables, expected_refs)
