"""Drop-in replacements for the standard output statement and `assign` and `echo` tags
that support inline `if` expressions.
"""
# pylint: disable=missing-class-docstring

from __future__ import annotations

import sys

from functools import partial

from typing import List
from typing import Optional

from liquid.context import Context

from liquid.expression import AssignmentExpression
from liquid.expression import Expression
from liquid.expression import FilteredExpression
from liquid.expression import Filter
from liquid.expression import is_truthy

from liquid.lex import _tokenize
from liquid.lex import _compile_rules
from liquid.lex import STRING_PATTERN
from liquid.lex import IDENTIFIER_PATTERN

from liquid.parse import expect
from liquid.parse import ExpressionParser

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.exceptions import Error
from liquid.exceptions import NoSuchFilterFunc
from liquid.exceptions import FilterValueError
from liquid.exceptions import LiquidSyntaxError

from liquid.token import TOKEN_ILLEGAL
from liquid.token import TOKEN_STATEMENT
from liquid.token import TOKEN_IDENTIFIER
from liquid.token import TOKEN_STRING
from liquid.token import TOKEN_INTEGER
from liquid.token import TOKEN_FLOAT
from liquid.token import TOKEN_EMPTY
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_BLANK
from liquid.token import TOKEN_NEGATIVE
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_CONTAINS
from liquid.token import TOKEN_PIPE
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_COMMA
from liquid.token import TOKEN_DOT
from liquid.token import TOKEN_LBRACKET
from liquid.token import TOKEN_RBRACKET
from liquid.token import TOKEN_AND
from liquid.token import TOKEN_OR
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION

from liquid.builtin.statement import StatementNode

from liquid.builtin.tags.assign_tag import TAG_ASSIGN
from liquid.builtin.tags.assign_tag import RE_ASSIGNMENT
from liquid.builtin.tags.assign_tag import AssignNode

from liquid.builtin.tags.echo_tag import TAG_ECHO
from liquid.builtin.tags.echo_tag import EchoNode

TOKEN_ELSE = sys.intern("else")
TOKEN_IF = sys.intern("if")

if_expression_rules = (
    (TOKEN_FLOAT, r"\d+\.\d*"),
    (TOKEN_INTEGER, r"\d+"),
    (TOKEN_NEGATIVE, r"-"),
    (TOKEN_STRING, STRING_PATTERN),
    (TOKEN_IDENTIFIER, IDENTIFIER_PATTERN),
    (TOKEN_DOT, r"\."),
    (TOKEN_COMMA, r","),
    (TOKEN_LBRACKET, r"\["),
    (TOKEN_RBRACKET, r"]"),
    (TOKEN_COLON, r":"),
    (TOKEN_PIPE, r"\|"),
    ("NEWLINE", r"\n"),
    ("OP", r"[!=<>]{1,2}"),
    ("SKIP", r"[ \t]+"),
    (TOKEN_ILLEGAL, r"."),
)

if_expression_keywords = frozenset(
    [
        TOKEN_TRUE,
        TOKEN_FALSE,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_EMPTY,
        TOKEN_BLANK,
        TOKEN_AND,
        TOKEN_OR,
        TOKEN_CONTAINS,
        TOKEN_ELSE,
        TOKEN_IF,
    ]
)

tokenize_if_expression = partial(
    _tokenize,
    rules=_compile_rules(if_expression_rules),
    keywords=if_expression_keywords,
)


class FilteredIfExpression(FilteredExpression):
    def __init__(
        self,
        expression: Expression,
        filters: Optional[List[Filter]] = None,
        condition: Optional[Expression] = None,
        alternative: Optional[Expression] = None,
        tail_filters: Optional[List[Filter]] = None,
    ):
        super().__init__(expression, filters)
        self.expression = expression
        self.condition = condition
        self.alternative = alternative
        self.filters = filters or []
        self.tail_filters = tail_filters or []

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, FilteredIfExpression)
            and self.expression == other.expression
            and self.condition == other.condition
            and self.alternative == other.alternative
            and self.filters == other.filters
        )

    def __str__(self) -> str:
        buf = [str(self.expression)]

        if self.filters:
            buf.append("|")
            buf.append(" | ".join([str(filter) for filter in self.filters]))

        if self.condition:
            buf.append("if")
            buf.append(str(self.condition))

        if self.alternative:
            buf.append("else")
            buf.append(str(self.alternative))

        if self.tail_filters:
            buf.append("|")
            buf.append(" | ".join([str(filter) for filter in self.tail_filters]))

        return " ".join(buf)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"FilteredIfExpression(expression={self.expression!r}, "
            f"condition={self.condition}, "
            f"alternative={self.alternative}, "
            f"filters={self.filters})"
        )

    def _apply_filters(
        self,
        result: object,
        filters: List[Filter],
        context: Context,
    ) -> object:
        for fltr in filters:
            try:
                func = context.filter(fltr.name)
            except NoSuchFilterFunc:
                if context.env.strict_filters:
                    raise
                continue

            # Any exception causes us to abort the filter chain and discard the result.
            # Nothing will be rendered.
            try:
                args = fltr.evaluate_args(context)
                kwargs = fltr.evaluate_kwargs(context)
                result = func(result, *args, **kwargs)
            except FilterValueError:
                # Pass over filtered expressions who's left value is not allowed.
                continue
            except Error:
                raise
            except Exception as err:
                raise Error(f"filter '{fltr.name}': unexpected error: {err}") from err

        return result

    async def _apply_filters_async(
        self, result: object, filters: List[Filter], context: Context
    ) -> object:
        for fltr in filters:
            try:
                func = context.filter(fltr.name)
            except NoSuchFilterFunc:
                if context.env.strict_filters:
                    raise
                continue

            # Any exception causes us to abort the filter chain and discard the result.
            # Nothing will be rendered.
            try:
                args = await fltr.evaluate_args_async(context)
                kwargs = await fltr.evaluate_kwargs_async(context)
                result = func(result, *args, **kwargs)
            except FilterValueError:
                # Pass over filtered expressions who's left value is not allowed.
                continue
            except Error:
                raise
            except Exception as err:
                raise Error(f"filter '{fltr.name}': unexpected error: {err}") from err

        return result

    def evaluate(self, context: Context) -> object:
        if self.condition:
            if is_truthy(self.condition.evaluate(context)):
                result = self.expression.evaluate(context)
                if self.filters:
                    result = self._apply_filters(result, self.filters, context)
            elif self.alternative:
                result = self.alternative.evaluate(context)
            else:
                result = context.env.undefined("")
        else:
            result = self.expression.evaluate(context)
            if self.filters:
                result = self._apply_filters(result, self.filters, context)

        if self.tail_filters:
            result = self._apply_filters(result, self.tail_filters, context)

        return result

    async def evaluate_async(self, context: Context) -> object:
        if self.condition:
            if is_truthy(await self.condition.evaluate_async(context)):
                result = await self.expression.evaluate_async(context)
                if self.filters:
                    result = await self._apply_filters_async(
                        result, self.filters, context
                    )
            elif self.alternative:
                result = await self.alternative.evaluate_async(context)
            else:
                result = context.env.undefined("")
        else:
            result = await self.expression.evaluate_async(context)
            if self.filters:
                result = await self._apply_filters_async(result, self.filters, context)

        if self.tail_filters:
            result = await self._apply_filters_async(result, self.tail_filters, context)

        return result

    def children(self) -> List[Expression]:
        _children = [self.expression]
        for fltr in self.filters:
            _children.extend(fltr.args)
            _children.extend(fltr.kwargs.values())

        if self.condition is not None:
            _children.append(self.condition)

        if self.alternative is not None:
            _children.append(self.alternative)

        for fltr in self.tail_filters:
            _children.extend(fltr.args)
            _children.extend(fltr.kwargs.values())

        return _children


class IfExpressionParser(ExpressionParser):
    """A specialization of the built-in expression parser that handles standard filtered
    expressions and adds support for inline `if` expressions."""

    END_EXPRESSION = (
        TOKEN_PIPE,
        TOKEN_COMMA,
        TOKEN_EOF,
        TOKEN_IF,
        TOKEN_ELSE,
    )

    def parse_filters(self, stream: TokenStream) -> List[Filter]:
        """Keep reading filters from the token stream until end of expression."""
        filters: List[Filter] = []
        while stream.current.type not in (TOKEN_EOF, TOKEN_IF):
            filters.append(self.parse_filter(stream))
        return filters

    def parse_filtered_if_expression(self, stream: TokenStream) -> FilteredIfExpression:
        """Parse a filtered expression with an optional inline ``if`` and ``else``."""
        expr = self.parse_expression(stream)
        stream.next_token()

        if stream.current.type == TOKEN_PIPE:
            filters = self.parse_filters(stream)
        else:
            filters = []

        if stream.current.type == TOKEN_IF:
            stream.next_token()  # Eat `if` token
            condition: Optional[Expression] = self.parse_boolean_expression(stream)
            stream.next_token()

            if stream.current.type == TOKEN_ELSE:
                stream.next_token()  # Eat `else` token
                alternative: Optional[Expression] = self.parse_expression(stream)
                stream.next_token()
            else:
                alternative = None
        else:
            assert stream.current.type in (TOKEN_EOF, TOKEN_PIPE)
            condition = None
            alternative = None

        tail_filters = self.parse_filters(stream)

        return FilteredIfExpression(
            expression=expr,
            filters=filters,
            condition=condition,
            alternative=alternative,
            tail_filters=tail_filters,
        )


parser = IfExpressionParser()


class InlineIfStatement(Tag):
    """A drop-in replacement for the standard output statement that supports inline
    `if` expressions."""

    name = TOKEN_STATEMENT

    def parse(self, stream: TokenStream) -> StatementNode:
        tok = stream.current
        expect(stream, TOKEN_STATEMENT)

        expr_iter = tokenize_if_expression(tok.value)
        node = StatementNode(
            tok, parser.parse_filtered_if_expression(TokenStream(expr_iter))
        )
        return node


class InlineIfAssignTag(Tag):
    """A drop-in replacement for the standard `assign` tag that supports inline `if`
    expressions."""

    name = TAG_ASSIGN
    block = False

    def parse(self, stream: TokenStream) -> AssignNode:
        expect(stream, TOKEN_TAG, value=TAG_ASSIGN)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)

        match = RE_ASSIGNMENT.match(stream.current.value)
        if match:
            name, expression = match.groups()
        else:
            raise LiquidSyntaxError(
                f'invalid assignment expression "{stream.current.value}"',
                linenum=stream.current.linenum,
            )

        expr_iter = tokenize_if_expression(expression)
        expr = parser.parse_filtered_if_expression(TokenStream(expr_iter))
        return AssignNode(tok, AssignmentExpression(name, expr))


class InlineIfEchoTag(Tag):
    """A drop-in replacement for the standard `echo` tag that supports inline `if`
    expressions."""

    name = TAG_ECHO
    block = False

    def parse(self, stream: TokenStream) -> EchoNode:
        expect(stream, TOKEN_TAG, value=TAG_ECHO)
        tok = stream.current
        stream.next_token()

        expect(stream, TOKEN_EXPRESSION)
        expr_iter = tokenize_if_expression(stream.current.value)

        expr = parser.parse_filtered_if_expression(TokenStream(expr_iter))
        return EchoNode(tok, expression=expr)
