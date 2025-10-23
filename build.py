from extra.extensions.katex import katex
from extra.extensions.aside import aside

from pyndakaas import Handler, handler, process_dir
import mistune

from pathlib import Path
from fnmatch import fnmatch


markdown = mistune.create_markdown(plugins=[katex, aside])

@handler()
class Markdown(Handler):
    template = 'post'

    @staticmethod
    def should_handle(source_path: Path) -> bool:
        return source_path.suffix == '.md'

    def transform(self) -> None:
        body = markdown(self.source)
        assert isinstance(body, str)
        self.body = body


process_dir(Path('src'), Path('build'))
