from pyndakaas import Handler, handler, process_dir
import mistune
from extensions.katex import katex
from extensions.aside import aside
from pathlib import Path


markdown = mistune.create_markdown(plugins=[katex, aside])

@handler()
class Markdown(Handler):
    @staticmethod
    def should_handle(source_path: Path) -> bool:
        return source_path.suffix == '.md'

    def template(self) -> str:
        return 'post'

    def body(self) -> str:
        output = markdown(self.source)
        assert isinstance(output, str)
        return output


process_dir(Path('src'), Path('build'))
