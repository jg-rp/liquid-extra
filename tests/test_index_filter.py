"""Test cases for the `index` filter."""
# pylint: disable=missing-class-docstring,missing-function-docstring

from dataclasses import dataclass

from liquid import Environment
from liquid.loaders import DictLoader

from liquid_extra.filters import index

from .base import FilterTestCase
from .base import RenderFilterTestCase
from .base import Case
from .base import RenderCase


@dataclass
class MockObject:
    name: str
    age: int


class IndexFilterTestCase(FilterTestCase):
    """Test the Index template filter."""

    def test_index_filter(self) -> None:
        test_cases = [
            Case(
                description="array of strings",
                val=["a", "b", "c"],
                args=["b"],
                kwargs={},
                expect=1,
            ),
            Case(
                description="array of strings item does not exist",
                val=["a", "b", "c"],
                args=["z"],
                kwargs={},
                expect=None,
            ),
            Case(
                description="array of objects",
                val=[
                    MockObject("Foo", 25),
                    MockObject("Bar", 33),
                    MockObject("Baz", 60),
                ],
                args=[MockObject("Baz", 60)],
                kwargs={},
                expect=2,
            ),
        ]

        self.env.add_filter("index", index)
        self._test(self.ctx.filter("index"), test_cases)


class RenderIndexFilterTestCase(RenderFilterTestCase):
    """Test the Index filter from a template."""

    def test_render_index_filter(self) -> None:
        test_cases = [
            RenderCase(
                description="array of strings",
                template=r"{{ handles | index: 'foo' }}",
                expect="0",
                globals={"handles": ["foo", "bar"]},
                partials={},
            ),
            RenderCase(
                description="array of strings item does not exist",
                template=r"{{ handles | index: 'baz' }}",
                expect="",
                globals={"handles": ["foo", "bar"]},
                partials={},
            ),
        ]

        for case in test_cases:
            env = Environment()
            env.add_filter("index", index)
            env.loader = DictLoader(case.partials)
            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)
