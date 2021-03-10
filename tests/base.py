import unittest

from inspect import isclass

from typing import NamedTuple
from typing import Any
from typing import List
from typing import Dict
from typing import Iterable
from typing import Callable
from typing import Mapping

from liquid.environment import Environment

from liquid import Context
from liquid.filter import Filter
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
    expect: str
    globals: Mapping[str, Any]
    partials: Mapping[str, Any]


class FilterTestCase(unittest.TestCase):
    def setUp(self):
        self.env = Environment()
        self.ctx = Context(self.env)

    def _test(self, fltr: Callable, test_cases: Iterable[Case]):
        for case in test_cases:
            with self.subTest(msg=case.description):
                if isclass(case.expect) and issubclass(case.expect, Exception):
                    with self.assertRaises(case.expect):
                        fltr(case.val, *case.args, **case.kwargs)
                else:
                    self.assertEqual(
                        fltr(case.val, *case.args, **case.kwargs), case.expect
                    )


class RenderFilterTestCase(unittest.TestCase):
    def setUp(self):
        self.env = Environment()

    def _test(self, fltr: Filter, test_cases: Iterable[RenderCase]):
        for case in test_cases:
            self.env.loader = DictLoader(case.partials)
            self.env.add_filter(fltr.name, fltr)

            template = self.env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)
