from __future__ import annotations

import sys

from functools import partial
from typing import TYPE_CHECKING

from liquid.lex import _tokenize
from liquid.lex import _compile_rules
from liquid.lex import STRING_PATTERN
from liquid.lex import boolean_expression_keywords

from liquid.parse import expect
from liquid.parse import ExpressionParser
from liquid.parse import Precedence

from liquid.context import Context
from liquid.exceptions import LiquidTypeError

from liquid.expression import PrefixExpression
from liquid.expression import is_truthy

from liquid.stream import TokenStream

from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_LPAREN
from liquid.token import TOKEN_RPAREN
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_NEGATIVE
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_ILLEGAL

from liquid.builtin.tags.if_tag import IfTag

if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment
    from liquid.expression import Expression


TOKEN_NOT = sys.intern("not")

boolean_not_expression_rules = (
    (TOKEN_FLOAT, r"\d+\.\d*"),
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_NEGATIVE, r"-"),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_IDENTIFIER, r"\w[a-zA-Z0-9_\-?]*"),
    (TOKEN_DOT, r"\."),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_LPAREN, r"\("),
    (TOKEN_RPAREN, r"\)"),
    ("NEWLINE", r"\n"),
    ("OP", r"[!=<>]{1,2}"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
)


boolean_not_expression_keywords = frozenset([*boolean_expression_keywords, TOKEN_NOT])

tokenize_boolean_not_expression = partial(
    _tokenize,
    rules=_compile_rules(boolean_not_expression_rules),
    keywords=boolean_not_expression_keywords,
)


class NotPrefixExpression(PrefixExpression):
    def evaluate(self, context: Context):
        right = self.right.evaluate(context)

        if self.operator == "-":
            if isinstance(right, (int, float)):
                return -right
            raise LiquidTypeError(f"unknown operator {self.operator}{self.right}")

        if self.operator == TOKEN_NOT:
            return not is_truthy(right)

        raise LiquidTypeError(f"unknown operator {self.operator}")


class NotExpressionParser(ExpressionParser):
    def __init__(self):
        super().__init__()
        self.prefix_funcs[TOKEN_NOT] = self.parse_prefix_expression

        # For grouped expressions
        self.prefix_funcs[TOKEN_LPAREN] = self.parse_grouped_expression
        self.precedences[TOKEN_RPAREN] = Precedence.LOWEST

    def parse_prefix_expression(self, stream: TokenStream) -> NotPrefixExpression:
        tok = stream.current
        stream.next_token()

        exp = NotPrefixExpression(
            tok.value,
            right=self.parse_expression(stream, precedence=Precedence.PREFIX),
        )

        return exp

    def parse_grouped_expression(self, stream: TokenStream) -> Expression:
        stream.next_token()
        exp = self.parse_expression(stream)

        stream.next_token()
        while stream.current.type == TOKEN_RPAREN:
            stream.next_token()

        if stream.current.type != TOKEN_EOF:
            exp = self.parse_infix_expression(stream, left=exp)

        return exp


class IfNotTag(IfTag):
    """A drop-in replacement for the standard `if` tag that allows logical
    `not` operators in expressions."""

    def __init__(self, env: Environment):
        super().__init__(env)
        self.expression_parser = NotExpressionParser()

    def parse_expression(self, stream: TokenStream) -> Expression:
        expect(stream, TOKEN_EXPRESSION)
        expr_iter = tokenize_boolean_not_expression(stream.current.value)
        return self.expression_parser.parse_boolean_expression(TokenStream(expr_iter))
