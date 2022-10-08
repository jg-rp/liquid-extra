"""Test cases for the `if (not)` tag.."""
# pylint: disable=missing-class-docstring,missing-function-docstring,too-many-lines

from unittest import TestCase

from typing import Any
from typing import Dict
from typing import Iterable
from typing import Mapping
from typing import NamedTuple


from liquid.context import Context
from liquid.environment import Environment
from liquid.loaders import DictLoader
from liquid.stream import TokenStream
from liquid import Mode
from liquid.exceptions import Error

from liquid.expression import BooleanExpression
from liquid.expression import IdentifierPathElement
from liquid.expression import Identifier
from liquid.expression import Boolean
from liquid.expression import StringLiteral
from liquid.expression import IntegerLiteral
from liquid.expression import FloatLiteral
from liquid.expression import PrefixExpression
from liquid.expression import InfixExpression

from liquid.golden.if_tag import cases as golden_cases

from liquid.token import Token
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_EQ
from liquid.token import TOKEN_NE
from liquid.token import TOKEN_LG
from liquid.token import TOKEN_GT
from liquid.token import TOKEN_LE
from liquid.token import TOKEN_GE
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_RANGE

from liquid_extra.tags.if_not import tokenize_boolean_not_expression
from liquid_extra.tags.if_not import NotExpressionParser
from liquid_extra.tags.if_not import NotPrefixExpression
from liquid_extra.tags.if_not import TOKEN_NOT
from liquid_extra.tags.if_not import TOKEN_RANGELPAREN

from liquid_extra.tags import IfNotTag


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
    partials: Dict[str, str] = {}


class BooleanLexerTestCase(TestCase):
    def test_lex_boolean_expression(self) -> None:
        """Test that we can tokenize comparison expressions."""
        test_cases = [
            LexerCase(
                "literal boolean",
                "false == true",
                [
                    Token(1, TOKEN_FALSE, "false"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_TRUE, "true"),
                ],
            ),
            LexerCase(
                "not nil identifier",
                "user != nil",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_NE, "!="),
                    Token(1, TOKEN_NIL, "nil"),
                ],
            ),
            LexerCase(
                "alternate not nil",
                "user <> nil",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_LG, "<>"),
                    Token(1, TOKEN_NIL, "nil"),
                ],
            ),
            LexerCase(
                "identifier equals string literal",
                "user.name == 'brian'",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_STRING, "brian"),
                ],
            ),
            LexerCase(
                "equality with or",
                "user.name == 'bill' or user.name == 'bob'",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_STRING, "bill"),
                    Token(1, TOKEN_OR, "or"),
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_STRING, "bob"),
                ],
            ),
            LexerCase(
                "equality with and",
                "user.name == 'bob' and user.age > 45",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "name"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_STRING, "bob"),
                    Token(1, TOKEN_AND, "and"),
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "age"),
                    Token(1, TOKEN_GT, ">"),
                    Token(1, TOKEN_INTEGER, "45"),
                ],
            ),
            LexerCase(
                "greater than or equal to integer literal",
                "user.age >= 21",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "age"),
                    Token(1, TOKEN_GE, ">="),
                    Token(1, TOKEN_INTEGER, "21"),
                ],
            ),
            LexerCase(
                "less than or equal to integer literal",
                "user.age <= 21",
                [
                    Token(1, TOKEN_IDENTIFIER, "user"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "age"),
                    Token(1, TOKEN_LE, "<="),
                    Token(1, TOKEN_INTEGER, "21"),
                ],
            ),
            LexerCase(
                "identifier contains string",
                "product.tags contains 'sale'",
                [
                    Token(1, TOKEN_IDENTIFIER, "product"),
                    Token(1, TOKEN_DOT, "."),
                    Token(1, TOKEN_IDENTIFIER, "tags"),
                    Token(1, TOKEN_CONTAINS, "contains"),
                    Token(1, TOKEN_STRING, "sale"),
                ],
            ),
            LexerCase(
                "literal boolean not true",
                "false == not true",
                [
                    Token(1, TOKEN_FALSE, "false"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_NOT, "not"),
                    Token(1, TOKEN_TRUE, "true"),
                ],
            ),
            LexerCase(
                "literal boolean not false",
                "false == not false",
                [
                    Token(1, TOKEN_FALSE, "false"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_NOT, "not"),
                    Token(1, TOKEN_FALSE, "false"),
                ],
            ),
            LexerCase(
                "parens",
                "(false and false)",
                [
                    Token(1, TOKEN_LPAREN, "("),
                    Token(1, TOKEN_FALSE, "false"),
                    Token(1, TOKEN_AND, "and"),
                    Token(1, TOKEN_FALSE, "false"),
                    Token(1, TOKEN_RPAREN, ")"),
                ],
            ),
            LexerCase(
                "range literals",
                "(1..3) == (1..3)",
                [
                    Token(1, TOKEN_RANGELPAREN, "("),
                    Token(1, TOKEN_INTEGER, "1"),
                    Token(1, TOKEN_RANGE, ".."),
                    Token(1, TOKEN_INTEGER, "3"),
                    Token(1, TOKEN_RPAREN, ")"),
                    Token(1, TOKEN_EQ, "=="),
                    Token(1, TOKEN_RANGELPAREN, "("),
                    Token(1, TOKEN_INTEGER, "1"),
                    Token(1, TOKEN_RANGE, ".."),
                    Token(1, TOKEN_INTEGER, "3"),
                    Token(1, TOKEN_RPAREN, ")"),
                ],
            ),
        ]

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = list(tokenize_boolean_not_expression(case.source))

                self.assertTrue(len(tokens) == len(case.expect))

                for got, want in zip(tokens, case.expect):
                    self.assertEqual(got, want)


class BooleanExpressionParserTestCase(TestCase):
    """Liquid expression parser test cases."""

    def _test(
        self,
        test_cases: Iterable[ParserCase],
        lex_func: Any,
        parse_func: Any,
    ) -> None:
        """Helper method for testing lists of Cases."""

        for case in test_cases:
            with self.subTest(msg=case.description):
                tokens = TokenStream(lex_func(case.expression))
                expr = parse_func(tokens)
                self.assertEqual(expr, case.expect)

    def test_parse_boolean_expression(self) -> None:
        """Test that we can parse boolean expressions."""
        test_cases = [
            ParserCase(
                "string literal double quotes",
                '"foobar"',
                BooleanExpression(
                    expression=StringLiteral("foobar"),
                ),
            ),
            ParserCase(
                "integer literal",
                "7",
                BooleanExpression(
                    expression=IntegerLiteral(7),
                ),
            ),
            ParserCase(
                "negative integer literal statement expression",
                "-7",
                BooleanExpression(
                    expression=PrefixExpression(
                        "-",
                        right=IntegerLiteral(7),
                    ),
                ),
            ),
            ParserCase(
                "float literal statement expression",
                "3.14",
                BooleanExpression(
                    expression=FloatLiteral(3.14),
                ),
            ),
            ParserCase(
                "negative float literal statement expression",
                "-3.14",
                BooleanExpression(
                    expression=NotPrefixExpression(
                        "-",
                        right=FloatLiteral(3.14),
                    ),
                ),
            ),
            ParserCase(
                "single identifier statement expression",
                "collection",
                BooleanExpression(
                    expression=Identifier(
                        path=[IdentifierPathElement("collection")],
                    ),
                ),
            ),
            ParserCase(
                "chained identifier",
                "collection.products",
                BooleanExpression(
                    expression=Identifier(
                        path=[
                            IdentifierPathElement("collection"),
                            IdentifierPathElement("products"),
                        ],
                    ),
                ),
            ),
            ParserCase(
                "keyword true",
                "true",
                BooleanExpression(
                    expression=Boolean(True),
                ),
            ),
            ParserCase(
                "keyword false",
                "false",
                BooleanExpression(
                    expression=Boolean(False),
                ),
            ),
            ParserCase(
                "boolean equality",
                "true == true",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="==",
                        right=Boolean(True),
                    ),
                ),
            ),
            ParserCase(
                "boolean inequality",
                "true != false",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="!=",
                        right=Boolean(False),
                    ),
                ),
            ),
            ParserCase(
                "boolean inequality alternate",
                "true <> false",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="<>",
                        right=Boolean(False),
                    ),
                ),
            ),
            ParserCase(
                "identifier greater than literal",
                "user.age > 21",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[
                                IdentifierPathElement("user"),
                                IdentifierPathElement("age"),
                            ],
                        ),
                        operator=">",
                        right=IntegerLiteral(21),
                    ),
                ),
            ),
            ParserCase(
                "identifier less than literal",
                "age < 18",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[IdentifierPathElement("age")],
                        ),
                        operator="<",
                        right=IntegerLiteral(18),
                    ),
                ),
            ),
            ParserCase(
                "identifier less than or equal to literal",
                "age <= 18",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[IdentifierPathElement("age")],
                        ),
                        operator="<=",
                        right=IntegerLiteral(18),
                    ),
                ),
            ),
            ParserCase(
                "identifier greater than or equal to literal",
                "age >= 18",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[IdentifierPathElement("age")],
                        ),
                        operator=">=",
                        right=IntegerLiteral(18),
                    ),
                ),
            ),
            ParserCase(
                "boolean or boolean",
                "true or false",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="or",
                        right=Boolean(False),
                    ),
                ),
            ),
            ParserCase(
                "identifier contains string",
                "product.tags contains 'sale'",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Identifier(
                            path=[
                                IdentifierPathElement("product"),
                                IdentifierPathElement("tags"),
                            ],
                        ),
                        operator="contains",
                        right=StringLiteral("sale"),
                    ),
                ),
            ),
            ParserCase(
                "not true",
                "not true",
                BooleanExpression(
                    expression=NotPrefixExpression(
                        "not",
                        right=Boolean(True),
                    ),
                ),
            ),
            ParserCase(
                "right associative",
                "true and false and false or true",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="and",
                        right=InfixExpression(
                            left=Boolean(False),
                            operator="and",
                            right=InfixExpression(
                                left=Boolean(False),
                                operator="or",
                                right=Boolean(True),
                            ),
                        ),
                    ),
                ),
            ),
            ParserCase(
                "grouped boolean",
                "(true and false and false) or true",
                BooleanExpression(
                    expression=InfixExpression(
                        left=InfixExpression(
                            left=Boolean(True),
                            operator="and",
                            right=InfixExpression(
                                left=Boolean(False),
                                operator="and",
                                right=Boolean(False),
                            ),
                        ),
                        operator="or",
                        right=Boolean(True),
                    ),
                ),
            ),
            ParserCase(
                "parens",
                "(true and false and false)",
                BooleanExpression(
                    expression=InfixExpression(
                        left=Boolean(True),
                        operator="and",
                        right=InfixExpression(
                            left=Boolean(False),
                            operator="and",
                            right=Boolean(False),
                        ),
                    ),
                ),
            ),
        ]

        expression_parser = NotExpressionParser()
        self._test(
            test_cases,
            tokenize_boolean_not_expression,
            expression_parser.parse_boolean_expression,
        )


class BooleanExpressionEvalTestCase(TestCase):
    """Boolean expression evaluator test cases."""

    def _test(
        self,
        test_cases: Iterable[EvalCase],
        lex_func: Any,
        parse_func: Any,
    ) -> None:
        """Utility method for evaluating lists of test cases."""
        env = Environment()

        for case in test_cases:
            context = Context(env, case.context)
            with self.subTest(msg=case.description):
                tokens = TokenStream(lex_func(case.expression))
                expr = parse_func(tokens)
                res = expr.evaluate(context)
                self.assertEqual(res, case.expect)

    def test_eval_boolean_expression(self) -> None:
        """Test that we can evaluate boolean expressions."""
        test_cases = [
            EvalCase(
                description="true literal",
                context={},
                expression="true",
                expect=True,
            ),
            EvalCase(
                description="false literal",
                context={},
                expression="false",
                expect=False,
            ),
            EvalCase(
                description="string literal",
                context={},
                expression="'some'",
                expect=True,
            ),
            EvalCase(
                description="empty string",
                context={},
                expression="''",
                expect=True,
            ),
            EvalCase(
                description="negative integer",
                context={},
                expression="-7",
                expect=True,
            ),
            EvalCase(
                description="truthy identifier",
                context={"collection": {"title": "foo"}},
                expression="collection.title",
                expect=True,
            ),
            EvalCase(
                description="falsey identifier",
                context={"collection": {"title": "foo"}},
                expression="collection.tags",
                expect=False,
            ),
            EvalCase(
                description="truthy comparision",
                context={"user": {"age": 21}},
                expression="user.age >= 21",
                expect=True,
            ),
            EvalCase(
                description="not equal comparision",
                context={"user": {"age": 21}},
                expression="user.age != 21",
                expect=False,
            ),
            EvalCase(
                description="truthy comparision and logic operator",
                context={
                    "user": {"age": 20},
                    "collection": {
                        "tags": [
                            "safe",
                        ]
                    },
                },
                expression="user.age >= 21 or collection.tags contains 'safe'",
                expect=True,
            ),
            EvalCase(
                description="boolean with logic operators",
                context={},
                expression="true and false and false or true",
                expect=False,
            ),
            EvalCase(
                description="empty array",
                context={"a": {"array": []}},
                expression="a.array == empty",
                expect=True,
            ),
            EvalCase(
                description="empty object",
                context={"a": {"obj": {}}},
                expression="a.obj == empty",
                expect=True,
            ),
            EvalCase(
                description="not empty array",
                context={"a": {"array": [1, 2]}},
                expression="a.array == empty",
                expect=False,
            ),
            EvalCase(
                description="not empty object",
                context={"a": {"obj": {"foo": "bar"}}},
                expression="a.obj == empty",
                expect=False,
            ),
            EvalCase(
                description="invalid comparison to empty",
                context={"a": {"foo": 1}},
                expression="a.foo == empty",
                expect=False,
            ),
            EvalCase(
                description="empty equals empty",
                context={},
                expression="empty == empty",
                expect=True,
            ),
            EvalCase(
                description="empty not equals true",
                context={},
                expression="empty != true",
                expect=True,
            ),
            EvalCase(
                description="nil equals nil",
                context={},
                expression="nil == nil",
                expect=True,
            ),
            EvalCase(
                description="string contains string",
                context={},
                expression="'hello' contains 'ell'",
                expect=True,
            ),
            EvalCase(
                description="string contains int",
                context={},
                expression="'hel1lo' contains 1",
                expect=True,
            ),
            EvalCase(
                description="string not equal int",
                context={},
                expression="'hello' != 1",
                expect=True,
            ),
            EvalCase(
                description="array contains",
                context={"foo": [1, 2, 4]},
                expression="foo contains 2",
                expect=True,
            ),
            EvalCase(
                description="array does not contain",
                context={"foo": [1, 2, 4]},
                expression="foo contains 3",
                expect=False,
            ),
            EvalCase(
                description="int equals",
                context={},
                expression="1 == 1",
                expect=True,
            ),
            EvalCase(
                description="int less than",
                context={},
                expression="1 < 2",
                expect=True,
            ),
            EvalCase(
                description="int less than or equal",
                context={},
                expression="1 <= 1",
                expect=True,
            ),
            EvalCase(
                description="int greater than",
                context={},
                expression="1 > 0",
                expect=True,
            ),
            EvalCase(
                description="int greater than or equal",
                context={},
                expression="1 >= 1",
                expect=True,
            ),
            EvalCase(
                description="true equals true",
                context={},
                expression="true == true",
                expect=True,
            ),
            EvalCase(
                description="true equal false",
                context={},
                expression="true == false",
                expect=False,
            ),
            EvalCase(
                description="true not equal false",
                context={},
                expression="true != false",
                expect=True,
            ),
            EvalCase(
                description="string equals int",
                context={},
                expression="'2' == 2",
                expect=False,
            ),
            EvalCase(
                description="empty string is truthy",
                context={},
                expression="''",
                expect=True,
            ),
            EvalCase(
                description="empty string and string is truthy",
                context={},
                expression="'' and 'foo'",
                expect=True,
            ),
            EvalCase(
                description="float equals int",
                context={},
                expression="1 == 1.0",
                expect=True,
            ),
            EvalCase(
                description="not true literal",
                context={},
                expression="not true",
                expect=False,
            ),
            EvalCase(
                description="not false literal",
                context={},
                expression="not false",
                expect=True,
            ),
            EvalCase(
                description="not nil literal",
                context={},
                expression="not nil",
                expect=True,
            ),
            EvalCase(
                description="not empty",
                context={},
                expression="not empty",
                expect=False,
            ),
            EvalCase(
                description="not string literal",
                context={},
                expression="not 'some'",
                expect=False,
            ),
            EvalCase(
                description="not empty string",
                context={},
                expression="not ''",
                expect=False,
            ),
            EvalCase(
                description="boolean with logic not operators",
                context={},
                expression="true and not false",
                expect=True,
            ),
            EvalCase(
                description="grouped boolean with logic operators",
                context={},
                expression="(true and false and false) or true",
                expect=True,
            ),
            EvalCase(
                description="nested grouped boolean with logic operators",
                context={},
                expression="((true or false) or (false)) and true",
                expect=True,
            ),
            EvalCase(
                description="grouped boolean with not",
                context={},
                expression="(true and false and false) or not true",
                expect=False,
            ),
            EvalCase(
                description="range literal equals range literal",
                context={},
                expression="(1..3) == (1..3)",
                expect=True,
            ),
        ]

        expression_parser = NotExpressionParser()
        self._test(
            test_cases,
            tokenize_boolean_not_expression,
            expression_parser.parse_boolean_expression,
        )


class BooleanRenderTestCases(TestCase):
    """Test cases for testing template renders."""

    def _test(self, test_cases: Iterable[RenderCase]) -> None:
        """Helper method for testing lists of test cases."""
        for case in test_cases:
            env = Environment(loader=DictLoader(case.partials))
            env.add_tag(IfNotTag)

            template = env.from_string(case.template, globals=case.globals)

            with self.subTest(msg=case.description):
                result = template.render()
                self.assertEqual(result, case.expect)

    def test_if_not_tag(self) -> None:
        """Test that we can render `if` tags."""
        test_cases = [
            RenderCase(
                description="condition with literal consequence",
                template=r"{% if product.title == 'foo' %}bar{% endif %}",
                expect="bar",
                globals={"product": {"title": "foo"}},
            ),
            RenderCase(
                description=(
                    "condition with literal consequence and literal alternative"
                ),
                template=(
                    r"{% if product.title == 'hello' %}bar{% else %}baz{% endif %}"
                ),
                expect="baz",
                globals={"product": {"title": "foo"}},
            ),
            RenderCase(
                description="condition with conditional alternative",
                template=(
                    r"{% if product.title == 'hello' %}"
                    r"foo"
                    r"{% elsif product.title == 'foo' %}"
                    r"bar"
                    r"{% endif %}"
                ),
                expect="bar",
                globals={"product": {"title": "foo"}},
            ),
            RenderCase(
                description=(
                    "condition with conditional alternative and final alternative"
                ),
                template=(
                    r"{% if product.title == 'hello' %}"
                    r"foo"
                    r"{% elsif product.title == 'goodbye' %}"
                    r"bar"
                    r"{% else %}"
                    r"baz"
                    r"{% endif %}"
                ),
                expect="baz",
                globals={"product": {"title": "foo"}},
            ),
            RenderCase(
                description="truthy-ness of a dictionary",
                template=r"{% if product %}bar{% else %}foo{% endif %}",
                expect="bar",
                globals={"product": {"title": "foo"}},
            ),
            RenderCase(
                description="falsey-ness of a literal nil",
                template=r"{% if nil %}bar{% else %}foo{% endif %}",
                expect="foo",
            ),
            RenderCase(
                description="falsey-ness of a non existant name",
                template=r"{% if nosuchthing %}bar{% else %}foo{% endif %}",
                expect="foo",
            ),
            RenderCase(
                description="nested condition in the consequence block",
                template=(
                    r"{% if product %}"
                    r"{% if title == 'Hello' %}baz{% endif %}"
                    r"{% endif %}"
                ),
                expect="baz",
                globals={
                    "product": {"title": "foo"},
                    "title": "Hello",
                },
            ),
            RenderCase(
                description="nested condition, alternative in the consequence block",
                template=(
                    r"{% if product %}"
                    r"{% if title == 'goodbye' %}"
                    r"baz"
                    r"{% else %}"
                    r"hello"
                    r"{% endif %}"
                    r"{% endif %}"
                ),
                expect="hello",
                globals={"product": {"title": "foo"}, "title": "Hello"},
            ),
            RenderCase(
                description="false",
                template=r"{% if false %}{% endif %}",
                expect="",
            ),
            RenderCase(
                description="contains condition",
                template=r"{% if product.tags contains 'garden' %}baz{% endif %}",
                expect="baz",
                globals={"product": {"tags": ["sports", "garden"]}},
            ),
            RenderCase(
                description="not equal condition",
                template=r"{% if product.title != 'foo' %}baz{% endif %}",
                expect="",
                globals={"product": {"title": "foo"}},
            ),
            RenderCase(
                description="alternate not equal condition",
                template=r"{% if product.title <> 'foo' %}baz{% endif %}",
                expect="",
                globals={"product": {"title": "foo"}},
            ),
            RenderCase(
                description="blank empty 'if'",
                template=r"{% if true %}  {% elsif false %} {% else %} {% endif %}",
                expect="",
            ),
            RenderCase(
                description="blank nested block",
                template=(
                    r"{% if true %} "
                    r"{% comment %} this is blank {% endcomment %} "
                    r"{% endif %}"
                ),
                expect="",
            ),
            RenderCase(
                description="not false",
                template=r"{% if not false %}foo{% endif %}",
                expect="foo",
            ),
            RenderCase(
                description="not true",
                template=r"{% if not true %}foo{% endif %}",
                expect="",
            ),
            RenderCase(
                description="literal boolean filter",
                template=r"{{ false | default: true }}",
                expect="true",
            ),
            RenderCase(
                description="not comparison to empty",
                template=r"{% if not '' == empty %}foo{% endif %}",
                expect="",
            ),
            RenderCase(
                description="not contains",
                template=r"{% if not foo contains 'z' %}bar{% endif %}",
                expect="bar",
                globals={"foo": ["a", "b", "c"]},
            ),
            RenderCase(
                description="and not",
                template=r"{% if not foo and not bar %}hello{% endif %}",
                expect="hello",
                globals={"foo": False, "bar": False},
            ),
            RenderCase(
                description="true and not",
                template=r"{% if foo and not bar %}hello{% endif %}",
                expect="hello",
                globals={"foo": True, "bar": False},
            ),
            RenderCase(
                description="not equals",
                template=r"{% if not foo == True %}hello{% endif %}",
                expect="hello",
                globals={"foo": False},
            ),
            RenderCase(
                description="not not equals False",
                template=r"{% if not foo != true %}hello{% endif %}",
                expect="",
                globals={"foo": False},
            ),
            RenderCase(
                description="not not equals true",
                template=r"{% if not foo != true %}hello{% endif %}",
                expect="hello",
                globals={"foo": True},
            ),
            RenderCase(
                description="not contains with parens",
                template=r"{% if not (foo contains 'z') %}bar{% endif %}",
                expect="bar",
                globals={"foo": ["a", "b", "c"]},
            ),
        ]

        self._test(test_cases)

    def test_golden_if(self) -> None:
        """Test liquid's golden test cases."""
        for case in golden_cases:
            env = Environment(
                loader=DictLoader(case.partials),
                tolerance=Mode.STRICT,
            )

            with self.subTest(msg=case.description):
                if case.error:
                    with self.assertRaises(Error):
                        template = env.from_string(case.template, globals=case.globals)
                        result = template.render()
                else:
                    template = env.from_string(case.template, globals=case.globals)
                    result = template.render()
                    self.assertEqual(result, case.expect)
