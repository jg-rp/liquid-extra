from dataclasses import dataclass

from liquid_extra.filters import Index

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

    def test_Index_filter(self):
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

        self.env.add_filter(Index.name, Index(self.env))
        self._test(self.ctx.filter(Index.name), test_cases)


class RenderIndexFilterTestCase(RenderFilterTestCase):
    """Test the Index filter from a template."""

    def test_render_Index_filter(self):
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

        self._test(Index(self.env), test_cases)
