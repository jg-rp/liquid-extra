"""Node and tag definitions for `with`."""
# pylint: disable=missing-class-docstring
from __future__ import annotations

import sys

from functools import partial

from typing import TYPE_CHECKING
from typing import Dict
from typing import List
from typing import NamedTuple
from typing import Optional
from typing import TextIO

from liquid.ast import ChildNode
from liquid.ast import Node
from liquid.ast import BlockNode

from liquid.context import Context
from liquid.expression import Expression

from liquid.lex import include_expression_rules
from liquid.lex import _compile_rules
from liquid.lex import _tokenize

from liquid.parse import expect
from liquid.parse import get_parser
from liquid.parse import parse_expression
from liquid.parse import parse_unchained_identifier

from liquid.stream import TokenStream
from liquid.tag import Tag

from liquid.token import Token
from liquid.token import TOKEN_TAG
from liquid.token import TOKEN_EXPRESSION
from liquid.token import TOKEN_TRUE
from liquid.token import TOKEN_FALSE
from liquid.token import TOKEN_NIL
from liquid.token import TOKEN_NULL
from liquid.token import TOKEN_COLON
from liquid.token import TOKEN_AS
from liquid.token import TOKEN_EOF
from liquid.token import TOKEN_COMMA


if TYPE_CHECKING:  # pragma: no cover
    from liquid import Environment

TAG_WITH = sys.intern("with")
TAG_ENDWITH = sys.intern("endwith")

with_expression_keywords = frozenset(
    [
        TOKEN_TRUE,
        TOKEN_FALSE,
        TOKEN_NIL,
        TOKEN_NULL,
        TOKEN_AS,
    ]
)

# We're borrowing token rules from the `include` tag, with our own set of valid
# keywords.
tokenize_with_expression = partial(
    _tokenize,
    rules=_compile_rules(include_expression_rules),
    keywords=with_expression_keywords,
)


class WithKeywordArg(NamedTuple):
    name: str
    expr: Expression


class WithNode(Node):
    def __init__(self, tok: Token, args: Dict[str, Expression], block: BlockNode):
        self.tok = tok
        self.args = args
        self.block = block

    def render_to_output(self, context: Context, buffer: TextIO) -> Optional[bool]:
        namespace = {k: v.evaluate(context) for k, v in self.args.items()}

        with context.extend(namespace):
            return self.block.render(context, buffer)

    async def render_to_output_async(
        self, context: Context, buffer: TextIO
    ) -> Optional[bool]:
        namespace = {k: await v.evaluate_async(context) for k, v in self.args.items()}
        with context.extend(namespace):
            return await self.block.render_async(context, buffer)

    def children(self) -> List[ChildNode]:
        return [
            ChildNode(
                linenum=self.tok.linenum, node=self.block, block_scope=list(self.args)
            ),
            *[
                ChildNode(linenum=self.tok.linenum, expression=expr)
                for expr in self.args.values()
            ],
        ]


class WithTag(Tag):
    name = TAG_WITH
    end = TAG_ENDWITH

    def __init__(self, env: Environment):
        super().__init__(env)
        self.parser = get_parser(self.env)

    def parse(self, stream: TokenStream) -> Node:
        expect(stream, TOKEN_TAG, value=TAG_WITH)
        tok = stream.current

        stream.next_token()
        expect(stream, TOKEN_EXPRESSION)
        expr_stream = TokenStream(tokenize_with_expression(stream.current.value))

        # A dictionary to help handle duplicate keywords.
        args = {}

        while expr_stream.current.type != TOKEN_EOF:
            key, expr = self.parse_argument(expr_stream)
            args[key] = expr

            if expr_stream.current.type == TOKEN_COMMA:
                expr_stream.next_token()  # Eat comma

        stream.next_token()
        block = self.parser.parse_block(stream, (TAG_ENDWITH, TOKEN_EOF))
        expect(stream, TOKEN_TAG, value=TAG_ENDWITH)

        return WithNode(tok=tok, args=args, block=block)

    def parse_argument(self, stream: TokenStream) -> WithKeywordArg:
        """Parse a keyword argument from a stream of tokens."""
        key = str(parse_unchained_identifier(stream))
        stream.next_token()

        expect(stream, TOKEN_COLON)
        stream.next_token()  # Eat colon

        val = parse_expression(stream)
        stream.next_token()

        return WithKeywordArg(key, val)
