from extra.extensions.katex import katex
from extra.extensions.aside import aside
from extra.parse import parse

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


@handler()
class Example(Handler):
    template = 'kotlinbyexample/example'

    @staticmethod
    def should_handle(input_path: Path) -> bool:
        result = input_path.is_dir() and fnmatch(str(input_path), 'src/kotlinbyexample/examples/*')
        return result

    def read_source(self):
        self.source = self.read_from_file(self.rel_input_path / 'main.kt')
        self.script_source = self.read_from_file(self.rel_input_path / 'run.sh')

    def initialize_extra_parameters(self):
        self.parameters['code'] = list(map(lambda x: (markdown(x[0]), x[1]), parse(self.source, '//')))
        self.parameters['script'] = list(map(lambda x: (markdown(x[0]), x[1]), parse(self.script_source, '#')))
        self.parameters['title'] = get_title(self.rel_input_path.name)
        pass

    def get_rel_output_path(self):
        return self.rel_input_path.parent.parent / self.rel_input_path.with_suffix('.html').name

@handler()
class Index(Handler):
    template = 'kotlinbyexample/index'
    examples = [
        'hello_world',
        'values'
    ]

    @staticmethod
    def should_handle(input_path: Path) -> bool:
        result = input_path.is_file() and fnmatch(str(input_path), 'src/kotlinbyexample/index')
        return result

    def initialize_extra_parameters(self) -> None:
        self.parameters['links'] = map(lambda x: (get_title(x), f'/kotlinbyexample/{x}'), self.examples)

    def transform(self) -> None:
        body = markdown(self.source)
        assert isinstance(body, str)
        self.body = body


def get_title(filename: str) -> str:
    return ' '.join(map(lambda w: w.capitalize(), filename.split('_')))


process_dir(Path('src'), Path('build'))
