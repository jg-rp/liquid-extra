"""Base test cases and table driven test helpers."""
# pylint: disable=missing-class-docstring,missing-function-docstring,too-many-lines
import unittest

from inspect import isclass

from typing import NamedTuple
from typing import Any
from typing import List
from typing import Dict
from typing import Iterable
from typing import Mapping
from typing import Union
from typing import Type

from liquid.environment import Environment

from liquid import Context
from liquid.loaders import DictLoader


class Case(NamedTuple):
    description: str
    val: Any
    args: List[Any]
    kwargs: Dict[Any, Any]
    expect: Any


class RenderCase(NamedTuple):
    description: str
    template: str
    expect: Union[str, Type[Exception]]
    globals: Mapping[str, Any]
    partials: Dict[str, Any]


class FilterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.env = Environment()
        self.ctx = Context(self.env)

    def _test(self, filter_: Any, test_cases: Iterable[Case]) -> None:
        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(case.expect, Exception):
                    with self.assertRaises(case.expect):
                        filter_(case.val, *case.args, **case.kwargs)
                else:
                    self.assertEqual(
                        filter_(case.val, *case.args, **case.kwargs), case.expect
                    )


class RenderFilterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.env = Environment()

    def _test(self, filter_: Any, test_cases: Iterable[RenderCase]) -> None:
        for case in test_cases:
            self.env.loader = DictLoader(case.partials)
            self.env.add_filter(filter_.name, filter_)

            template = self.env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(case.expect, Exception):
                    with self.assertRaises(case.expect):
                        template.render()
                else:
                    result = template.render()
                    self.assertEqual(result, case.expect)
