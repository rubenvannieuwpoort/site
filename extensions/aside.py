import re
from typing import Match
from mistune.markdown import Markdown
from mistune.block_parser import BlockParser
from mistune.core import BaseRenderer, BlockState


__all__ = ["aside"]


_ASIDE_START = re.compile(r"^ {0,3}! ?", re.M)
_ASIDE_MATCH = re.compile(r"^( {0,3}![^\n]*\n)+$")


def parse_aside(block: BlockParser, m: Match[str], state: BlockState) -> int:
    text, end_pos = block.extract_block_quote(m, state)
    if not text.endswith("\n"):
        # ensure it endswith \n to make sure
        # _ASIDE_MATCH.match works
        text += "\n"

    depth = state.depth()
    if not depth and _ASIDE_MATCH.match(text):
        text = _ASIDE_START.sub("", text)
        tok_type = "aside"
    else:
        tok_type = "block_quote"

    # scan children state
    child = state.child_state(text)
    if state.depth() >= block.max_nested_level - 1:
        rules = list(block.block_quote_rules)
        rules.remove("block_quote")
    else:
        rules = block.block_quote_rules

    block.parse(child, rules)
    token = {"type": tok_type, "children": child.tokens}
    if end_pos:
        state.prepend_token(token)
        return end_pos
    state.append_token(token)
    return state.cursor


def render_aside(renderer: BaseRenderer, text: str) -> str:
    return '<aside>\n' + text + "</aside>\n"


def aside(md: Markdown) -> None:
    """A mistune plugin to support asides. The
    syntax is inspired by stackexchange:

    .. code-block:: text

        Asides looks like block quote, but with `>!`:

        >! this is an aside
        >!
        >! it will be placed in a sidebar

    :param md: Markdown instance
    """
    # reset block quote parser with block spoiler parser
    md.block.register("block_quote", None, parse_aside)
    if md.renderer and md.renderer.NAME == "html":
        md.renderer.register("aside", render_aside)
