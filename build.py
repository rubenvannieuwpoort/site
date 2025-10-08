from pyndakaas import Handler, handler, renderer, process_dir
import mistune
from extensions.katex import katex
from extensions.aside import aside
from pathlib import Path

@handler()
class Markdown(Handler):
    suffix = '.html'
    template = 'post'
    renderer = 'markdown'

    @staticmethod
    def detect(source_path: Path) -> bool:
        return source_path.suffix == '.md'


markdown = mistune.create_markdown(plugins=[katex, aside])

@renderer("markdown")
def render_markdown(source: str) -> str:
    output = markdown(source)
    assert isinstance(output, str)
    return output

process_dir(Path('src'), Path('build'))
