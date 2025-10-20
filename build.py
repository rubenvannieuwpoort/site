from pyndakaas import Handler, handler, process_dir
import mistune
from extensions.katex import katex
from extensions.aside import aside
from pathlib import Path


markdown = mistune.create_markdown(plugins=[katex, aside])

@handler()
class Markdown(Handler):
    template = 'post'

    @staticmethod
    def should_handle(source_path: Path) -> bool:
        return source_path.suffix == '.md'

    def transform(self) -> None:
        self.body = markdown(self.source)


process_dir(Path('src'), Path('build'))
