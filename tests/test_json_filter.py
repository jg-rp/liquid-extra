"""Test cases for the `json` filter."""
# pylint: disable=missing-class-docstring,missing-function-docstring

from typing import Any
from typing import Dict

from dataclasses import dataclass
from dataclasses import is_dataclass
from dataclasses import asdict

from liquid.exceptions import FilterArgumentError

from liquid_extra.filters import JSON

from .base import FilterTestCase
from .base import RenderFilterTestCase
from .base import Case
from .base import RenderCase


@dataclass
class MockData:
    length: int
    width: int


class JSONFilterTestCase(FilterTestCase):
    """Test the JSON template filter."""

    def test_json_filter(self) -> None:
        test_cases = [
            Case(
                description="serialize a string",
                val="hello",
                args=[],
                kwargs={},
                expect='"hello"',
            ),
            Case(
                description="serialize an int",
                val=42,
                args=[],
                kwargs={},
                expect="42",
            ),
            Case(
                description="serialize a dict with list",
                val={"foo": [1, 2, 3]},
                args=[],
                kwargs={},
                expect='{"foo": [1, 2, 3]}',
            ),
            Case(
                description="serialize an arbitrary object",
                val={"foo": MockData(3, 4)},
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        self.env.add_filter(JSON.name, JSON())
        self._test(self.ctx.filter(JSON.name), test_cases)

    def test_json_with_encoder_func(self) -> None:
        test_cases = [
            Case(
                description="serialize a dataclass",
                val={"foo": MockData(3, 4)},
                args=[],
                kwargs={},
                expect=r'{"foo": {"length": 3, "width": 4}}',
            ),
            Case(
                description="serialize an arbitrary object",
                val={"foo": object()},
                args=[],
                kwargs={},
                expect=FilterArgumentError,
            ),
        ]

        def default(obj: object) -> Dict[str, Any]:
            if is_dataclass(obj):
                return asdict(obj)
            raise TypeError(f"can't serialize object {obj}")

        self.env.add_filter(JSON.name, JSON(default=default))
        self._test(self.ctx.filter(JSON.name), test_cases)


class RenderJSONFilterTestCase(RenderFilterTestCase):
    """Test the JSON filter from a template."""

    def test_render_json_filter(self) -> None:
        test_cases = [
            RenderCase(
                description="render a string literal as JSON",
                template=r"{{ 'hello' | json }}",
                expect='"hello"',
                globals={},
                partials={},
            ),
            RenderCase(
                description="render a tuple of ints",
                template=r"{{ dat | json }}",
                expect="[1, 2, 3]",
                globals={"dat": (1, 2, 3)},
                partials={},
            ),
        ]

        self._test(JSON(), test_cases)

    def test_render_json_with_encoder_func(self) -> None:
        test_cases = [
            RenderCase(
                description="render an arbitrary object as JSON",
                template=r"{{ foo | json }}",
                expect=FilterArgumentError,
                globals={"foo": object()},
                partials={},
            ),
            RenderCase(
                description="render a dataclass as JSON",
                template=r"{{ foo | json }}",
                expect=r'{"length": 3, "width": 4}',
                globals={"foo": MockData(3, 4)},
                partials={},
            ),
        ]

        def default(obj: object) -> Dict[str, Any]:
            if is_dataclass(obj):
                return asdict(obj)
            raise TypeError(f"can't serialize object {obj}")

        self._test(JSON(default=default), test_cases)
