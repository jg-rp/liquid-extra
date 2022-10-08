"""Test cases for `if` expression tags."""
# pylint: disable=missing-class-docstring,missing-function-docstring

import asyncio
import unittest

from typing import Any
from typing import Dict
from typing import Mapping
from typing import NamedTuple

from liquid import Environment
from liquid.context import Context

from liquid.exceptions import Error
from liquid.exceptions import NoSuchFilterFunc
from liquid.exceptions import FilterArgumentError
from liquid.exceptions import LiquidSyntaxError

from liquid.loaders import DictLoader
from liquid.parse import get_parser
from liquid.stream import TokenStream

from liquid.template import BoundTemplate
from liquid.template import Refs

from liquid.expression import Filter
from liquid.expression import Identifier
from liquid.expression import IdentifierPathElement
from liquid.expression import StringLiteral
from liquid.expression import BooleanExpression
from liquid.expression import TRUE

from liquid.token import Token
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_IDENTIFIER

from liquid_extra.tags.if_expressions import TOKEN_IF
from liquid_extra.tags.if_expressions import TOKEN_ELSE
from liquid_extra.tags.if_expressions import parser
from liquid_extra.tags.if_expressions import tokenize_if_expression
from liquid_extra.tags.if_expressions import FilteredIfExpression
from liquid_extra.tags.if_expressions import InlineIfStatement
from liquid_extra.tags.if_expressions import InlineIfAssignTag
from liquid_extra.tags.if_expressions import InlineIfEchoTag


class LexerCase(NamedTuple):
    description: str
    source: str
    expect: Any


class ParserCase(NamedTuple):
    description: str
    expression: str
    expect: Any


class EvalCase(NamedTuple):
    description: str
    context: Mapping[str, Any]
    expression: str
    expect: Any


class RenderCase(NamedTuple):
    description: str
    template: str
    expect: str
    globals: Mapping[str, Any] = {}
    partials: Dict[str, Any] = {}


class IfExpressionLexerTestCase(unittest.TestCase):
    """If expression lexer test case."""

    def test_lex_if_expression(self) -> None:
        """Test that we can tokenize inline `if` expressions."""
        test_cases = [
            LexerCase(
                description="standard expression, no if",
                source="'foo'",
                expect=[
                    Token(1, TOKEN_STRING, "foo"),
                ],
            ),
            LexerCase(
                description="standard expression with a filter, no if",
                source="'foo' | upcase ",
                expect=[
                    Token(1, TOKEN_STRING, "foo"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "upcase"),
                ],
            ),
            LexerCase(
                description="basic inline if",
                source="'foo' if true",
                expect=[
                    Token(1, TOKEN_STRING, "foo"),
                    Token(1, TOKEN_IF, "if"),
                ],
            ),
            LexerCase(
                description="basic inline if with alternative",
                source="'foo' if true else 'bar'",
                expect=[
                    Token(1, TOKEN_STRING, "foo"),
                    Token(1, TOKEN_IF, "if"),
                    Token(1, TOKEN_TRUE, "true"),
                    Token(1, TOKEN_ELSE, "else"),
                    Token(1, TOKEN_STRING, "bar"),
                ],
            ),
            LexerCase(
                description="inline if with filter",
                source="'foo' | upcase if true else 'bar'",
                expect=[
                    Token(1, TOKEN_STRING, "foo"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "upcase"),
                    Token(1, TOKEN_IF, "if"),
                    Token(1, TOKEN_TRUE, "true"),
                    Token(1, TOKEN_ELSE, "else"),
                    Token(1, TOKEN_STRING, "bar"),
                ],
            ),
            LexerCase(
                description="inline if with tail filter",
                source="'foo' if true else 'bar' | upcase",
                expect=[
                    Token(1, TOKEN_STRING, "foo"),
                    Token(1, TOKEN_IF, "if"),
                    Token(1, TOKEN_TRUE, "true"),
                    Token(1, TOKEN_ELSE, "else"),
                    Token(1, TOKEN_STRING, "bar"),
                    Token(1, TOKEN_PIPE, "|"),
                    Token(1, TOKEN_IDENTIFIER, "upcase"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_if_expression(case.source))
                self.assertTrue(len(tokens), len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)


class IfExpressionParserTestCase(unittest.TestCase):
    """If expression parser test case."""

    def test_parse_inline_if_expression(self) -> None:
        """Test that we can parse inline `if` expressions."""
        test_cases = [
            ParserCase(
                description="string literal",
                expression="'foo'",
                expect=FilteredIfExpression(expression=StringLiteral("foo")),
            ),
            ParserCase(
                description="string literal with filter",
                expression="'foo' | upcase",
                expect=FilteredIfExpression(
                    expression=StringLiteral("foo"),
                    filters=[Filter(name="upcase", args=[])],
                ),
            ),
            ParserCase(
                description="string literal with condition",
                expression="'foo' if true",
                expect=FilteredIfExpression(
                    expression=StringLiteral("foo"),
                    condition=BooleanExpression(expression=TRUE),
                ),
            ),
            ParserCase(
                description="string literal with condition and alternative",
                expression="'foo' if true else 'bar'",
                expect=FilteredIfExpression(
                    expression=StringLiteral("foo"),
                    condition=BooleanExpression(expression=TRUE),
                    alternative=StringLiteral("bar"),
                ),
            ),
            ParserCase(
                description="identifiers with condition and alternative",
                expression="products[0] if products else 'bar'",
                expect=FilteredIfExpression(
                    expression=Identifier(
                        path=[
                            IdentifierPathElement("products"),
                            IdentifierPathElement(0),
                        ]
                    ),
                    condition=BooleanExpression(
                        expression=Identifier(path=[IdentifierPathElement("products")])
                    ),
                    alternative=StringLiteral("bar"),
                ),
            ),
            ParserCase(
                description="string literal with condition, alternative and filter",
                expression="'foo' | upcase if true else 'bar'",
                expect=FilteredIfExpression(
                    expression=StringLiteral("foo"),
                    condition=BooleanExpression(expression=TRUE),
                    alternative=StringLiteral("bar"),
                    filters=[Filter(name="upcase", args=[])],
                ),
            ),
            ParserCase(
                description=(
                    "string literal with condition, alternative and tail filter"
                ),
                expression="'foo' if true else 'bar' | upcase",
                expect=FilteredIfExpression(
                    expression=StringLiteral("foo"),
                    condition=BooleanExpression(expression=TRUE),
                    alternative=StringLiteral("bar"),
                    tail_filters=[Filter(name="upcase", args=[])],
                ),
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = TokenStream(tokenize_if_expression(case.expression))
                expr = parser.parse_filtered_if_expression(tokens)
                self.assertEqual(expr, case.expect)

    def test_if_expression_string(self) -> None:
        """Test the string representation of an inline `if` expression."""
        tokens = TokenStream(
            tokenize_if_expression("'hello' | downcase if true else 'goodbye' | upcase")
        )
        expr = parser.parse_filtered_if_expression(tokens)
        self.assertEqual(
            str(expr), "'hello' | downcase if (True) else 'goodbye' | upcase"
        )


class IfExpressionEvalTestCase(unittest.TestCase):
    """If expression evaluation test case."""

    def test_evaluate_inline_if_expression(self) -> None:
        """Test that we correctly evaluate inline `if` expressions."""
        env = Environment()

        test_cases = [
            EvalCase(
                description="string literal",
                context={},
                expression="'foo'",
                expect="foo",
            ),
            EvalCase(
                description="string literal with true condition",
                context={},
                expression="'foo' if true",
                expect="foo",
            ),
            EvalCase(
                description="string literal with false condition",
                context={},
                expression="'foo' if false",
                expect=env.undefined(""),
            ),
            EvalCase(
                description="string literal with false condition and alternative",
                context={},
                expression="'foo' if false else 'bar'",
                expect="bar",
            ),
            EvalCase(
                description="object and condition from context",
                context={"settings": {"foo": True}, "greeting": "hello"},
                expression="greeting if settings.foo else 'bar'",
                expect="hello",
            ),
            EvalCase(
                description="object and condition from context with tail filter",
                context={"settings": {"foo": True}, "greeting": "hello"},
                expression="greeting if settings.foo else 'bar' | upcase",
                expect="HELLO",
            ),
            EvalCase(
                description="object filter with true condition",
                context={},
                expression="'foo' | upcase if true else 'bar'",
                expect="FOO",
            ),
            EvalCase(
                description="object filter with false condition",
                context={},
                expression="'foo' | upcase if false else 'bar'",
                expect="bar",
            ),
        ]

        for case in test_cases:
            context = Context(env, case.context)
            with self.subTest(msg=case.description):
                tokens = TokenStream(tokenize_if_expression(case.expression))
                expr = parser.parse_filtered_if_expression(tokens)
                res = expr.evaluate(context)
                self.assertEqual(res, case.expect)


class IfExpressionRenderTextCase(unittest.TestCase):
    """If expression render test case."""

    def test_render_statement_inline_if_expression(self) -> None:
        """Test that we correctly render output statements that use inline `if`."""
        test_cases = [
            RenderCase(
                description="string literal",
                template=r"{{ 'hello' }}",
                expect="hello",
                globals={},
                partials={},
            ),
            RenderCase(
                description="string literal with true condition",
                template=r"{{ 'hello' if true }}",
                expect="hello",
                globals={},
                partials={},
            ),
            RenderCase(
                description="default to undefined",
                template=r"{{ 'hello' if false }}",
                expect="",
                globals={},
                partials={},
            ),
            RenderCase(
                description="early  filter",
                template=r"{{ 'hello' | upcase if true }}",
                expect="HELLO",
                globals={},
                partials={},
            ),
            RenderCase(
                description="string literal with false condition and alternative",
                template=r"{{ 'hello' if false else 'goodbye' }}",
                expect="goodbye",
                globals={},
                partials={},
            ),
            RenderCase(
                description="object and condition from context with tail filter",
                template=r"{{ greeting if settings.foo else 'bar' | upcase }}",
                expect="HELLO",
                globals={"settings": {"foo": True}, "greeting": "hello"},
                partials={},
            ),
        ]

        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            env.add_tag(InlineIfStatement)
            get_parser.cache_clear()  # Necessary prior to Liquid version 0.8.2.

            with self.subTest(msg=case.description):
                template = env.from_string(case.template, globals=case.globals)
                result = template.render()
                self.assertEqual(result, case.expect)

        # Same again using async path.

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            env.add_tag(InlineIfStatement)
            get_parser.cache_clear()  # Necessary prior to Liquid version 0.8.2.

            with self.subTest(msg=case.description):
                template = env.from_string(case.template, globals=case.globals)
                result = asyncio.run(coro(template))
                self.assertEqual(result, case.expect)

    def test_render_assign_inline_if_expression(self) -> None:
        """Test that we correctly render assignment expressions that use inline `if`."""
        test_cases = [
            RenderCase(
                description="string literal",
                template=r"{% assign foo = 'hello' %}{{ foo }}",
                expect="hello",
                globals={},
                partials={},
            ),
            RenderCase(
                description="string literal with true condition",
                template=r"{% assign foo = 'hello' if true %}{{ foo }}",
                expect="hello",
                globals={},
                partials={},
            ),
            RenderCase(
                description="default to undefined",
                template=r"{% assign foo = 'hello' if false %}{{ foo }}",
                expect="",
                globals={},
                partials={},
            ),
            RenderCase(
                description="early  filter",
                template=r"{% assign foo = 'hello' | upcase if true %}{{ foo }}",
                expect="HELLO",
                globals={},
                partials={},
            ),
            RenderCase(
                description="string literal with false condition and alternative",
                template=r"{% assign foo = 'hello' if false else 'goodbye' %}{{ foo }}",
                expect="goodbye",
                globals={},
                partials={},
            ),
            RenderCase(
                description="object and condition from context with tail filter",
                template=(
                    r"{% assign foo = greeting if settings.foo else 'bar' | upcase %}"
                    r"{{ foo }}"
                ),
                expect="HELLO",
                globals={"settings": {"foo": True}, "greeting": "hello"},
                partials={},
            ),
        ]

        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            env.add_tag(InlineIfAssignTag)

            with self.subTest(msg=case.description):
                template = env.from_string(case.template, globals=case.globals)
                result = template.render()
                self.assertEqual(result, case.expect)

        # Same again using async path.

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            env.add_tag(InlineIfAssignTag)

            with self.subTest(msg=case.description):
                template = env.from_string(case.template, globals=case.globals)
                result = asyncio.run(coro(template))
                self.assertEqual(result, case.expect)

    def test_render_echo_inline_if_expression(self) -> None:
        """Test that we correctly render echo expressions that use inline `if`."""
        test_cases = [
            RenderCase(
                description="string literal",
                template=r"{% echo 'hello' %}",
                expect="hello",
                globals={},
                partials={},
            ),
            RenderCase(
                description="string literal with true condition",
                template=r"{% echo 'hello' if true %}",
                expect="hello",
                globals={},
                partials={},
            ),
            RenderCase(
                description="default to undefined",
                template=r"{% echo 'hello' if false %}",
                expect="",
                globals={},
                partials={},
            ),
            RenderCase(
                description="early  filter",
                template=r"{% echo 'hello' | upcase if true %}",
                expect="HELLO",
                globals={},
                partials={},
            ),
            RenderCase(
                description="string literal with false condition and alternative",
                template=r"{% echo 'hello' if false else 'goodbye' %}",
                expect="goodbye",
                globals={},
                partials={},
            ),
            RenderCase(
                description="object and condition from context with tail filter",
                template=(r"{% echo greeting if settings.foo else 'bar' | upcase %}"),
                expect="HELLO",
                globals={"settings": {"foo": True}, "greeting": "hello"},
                partials={},
            ),
        ]

        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            env.add_tag(InlineIfEchoTag)

            with self.subTest(msg=case.description):
                template = env.from_string(case.template, globals=case.globals)
                result = template.render()
                self.assertEqual(result, case.expect)

        # Same again using async path.

        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            env.add_tag(InlineIfEchoTag)

            with self.subTest(msg=case.description):
                template = env.from_string(case.template, globals=case.globals)
                result = asyncio.run(coro(template))
                self.assertEqual(result, case.expect)

    def test_unknown_filter(self) -> None:
        """Test that unknown filters are handled properly."""
        env = Environment(strict_filters=True)
        env.add_tag(InlineIfStatement)

        template = env.from_string(r"{{ 'hello' | nosuchthing }}")

        with self.assertRaises(NoSuchFilterFunc):
            template.render()

        # and render async
        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        with self.assertRaises(NoSuchFilterFunc):
            asyncio.run(coro(template))

        env.strict_filters = False
        self.assertEqual(template.render(), "hello")
        self.assertEqual(asyncio.run(coro(template)), "hello")

    def test_filter_value_error(self) -> None:
        """Test unexpected filter values."""
        env = Environment()
        env.add_tag(InlineIfStatement)

        template = env.from_string(r"{{ 123 | first }}")

        self.assertEqual(template.render(), "")

        # and render async
        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        self.assertEqual(asyncio.run(coro(template)), "")

    def test_filter_argument_error(self) -> None:
        """Test unexpected filter arguments."""
        env = Environment()
        env.add_tag(InlineIfStatement)

        template = env.from_string(r"{{ 123 | divided_by: 0 }}")

        with self.assertRaises(FilterArgumentError):
            template.render()

        # and render async
        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        with self.assertRaises(FilterArgumentError):
            asyncio.run(coro(template))

    def test_unexpected_filter_exception(self) -> None:
        """Test unexpected filter exception."""
        env = Environment()
        env.add_tag(InlineIfStatement)

        def func() -> None:
            raise Exception(":(")

        env.add_filter("func", func)

        template = env.from_string(r"{{ 123 | func }}")

        with self.assertRaises(Error):
            template.render()

        # and render async
        async def coro(template: BoundTemplate) -> str:
            return await template.render_async()

        with self.assertRaises(Error):
            asyncio.run(coro(template))

    def test_assign_expression_syntax_error(self) -> None:
        """Test that we handle syntax errors in `assign` expressions using inline
        `if`."""
        env = Environment()
        env.add_tag(InlineIfAssignTag)

        with self.assertRaises(LiquidSyntaxError):
            env.from_string(r"{% assign foo.bar = 'hello' %}")


class AnalyzeIfExpressionTestCase(unittest.TestCase):
    def test_analyze_macro_tag(self) -> None:
        """Test that we can statically analyze macro and call tags."""
        env = Environment()
        env.add_tag(InlineIfStatement)

        template = env.from_string(r"{{ foo | upcase if a.b else bar | append: baz }}")

        expected_template_globals = {
            "foo": [("<string>", 1)],
            "a.b": [("<string>", 1)],
            "bar": [("<string>", 1)],
            "baz": [("<string>", 1)],
        }
        expected_template_locals: Refs = {}
        expected_refs = {
            "foo": [("<string>", 1)],
            "a.b": [("<string>", 1)],
            "bar": [("<string>", 1)],
            "baz": [("<string>", 1)],
        }

        analysis = template.analyze()

        self.assertEqual(analysis.local_variables, expected_template_locals)
        self.assertEqual(analysis.global_variables, expected_template_globals)
        self.assertEqual(analysis.variables, expected_refs)
