import pykatex

from mistune.core import BaseRenderer, BlockState, InlineState
from mistune.block_parser import BlockParser
from mistune.inline_parser import InlineParser
from typing import Match


BLOCK_MATH_PATTERN = r"\$\$(?P<math_text>[\s\S]+?)\$\$"
INLINE_MATH_PATTERN = r"(?<!\$)\$(?P<math_text>[^$\r\n]+?)\$(?!\$)"


def katex(md):
    md.block.register('block_math', BLOCK_MATH_PATTERN, parse_block_math, before='list')
    md.inline.register('inline_math', INLINE_MATH_PATTERN, parse_inline_math, before='link')
    if md.renderer and md.renderer.NAME == 'html':
        md.renderer.register('block_math', render_block_math)
        md.renderer.register('inline_math', render_inline_math)


def parse_block_math(_: BlockParser, m: Match[str], state: BlockState) -> int:
    text = m.group("math_text")
    state.append_token({"type": "block_math", "raw": text})
    return m.end() + 1


def render_block_math(_: BaseRenderer, text: str) -> str:
    return pykatex.renderToString(text, displayMode=True, output="html", strict=False)


def parse_inline_math(_: InlineParser, m: Match[str], state: InlineState) -> int:
    text = m.group("math_text")
    state.append_token({"type": "inline_math", "raw": text})
    return m.end()


def render_inline_math(_: BaseRenderer, text: str) -> str:
    return pykatex.renderToString(text, displayMode=False, output="html", strict=False)
