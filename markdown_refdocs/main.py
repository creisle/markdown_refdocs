import ast
from typing import List, Tuple
import os
import argparse

from .parsers import parse_google_docstring, left_align_block
from .markdown import function_md, argument_md


def get_lines_covered(node: ast.AST) -> Tuple[int, int]:
    lines = []
    if hasattr(node, 'lineno'):
        lines.append(node.lineno)
    for n in ast.walk(node):
        if hasattr(n, 'lineno'):
            lines.append(n.lineno)
    return min(lines), max(lines)


class ModuleAnalyzer(ast.NodeVisitor):
    def __init__(
        self,
        filename: str,
        prefix: str = '',
        hide_private: bool = True,
        hide_undoc: bool = True,
        hide_undoc_args: bool = True,
        namespace_headers: bool = False,
    ):
        print('processing module', filename)
        self.name = (
            filename.replace('.py', '').replace('/', '.')[len(prefix) :].replace('.__init__', '')
        )
        self.hide_private = hide_private
        self.hide_undoc = hide_undoc
        self.hide_undoc_args = hide_undoc_args
        self.namespace_headers = namespace_headers

        with open(filename, "r") as source:
            self.content = source.read()
            self.lines = self.content.split('\n')

    def get_qualified_name(self, node: ast.AST, name: str) -> str:
        parents = []
        if not node.parent:
            return None
        parent = node.parent
        while True:
            if not self.namespace_headers and isinstance(parent, ast.Module):
                break
            try:
                parents.append(parent.name)
                parent = parent.parent
            except Exception:
                break
        parents.reverse()
        return '.'.join(parents + [name])

    def get_source_segment(self, node: ast.AST, expected_end_char: str = None) -> str:
        # only builtin  in py3.8+ so re-implemented here
        start, end = get_lines_covered(node)
        content = '\n'.join(self.lines[start - 1 : end])
        if expected_end_char and not content.strip().endswith(expected_end_char):
            end += 1
            content = '\n'.join(self.lines[start - 1 : end])
        return content

    def get_function_def_segment(self, node: ast.AST) -> str:
        """
        Get the source code lines covering the function defintion
        """
        try:
            start, end = get_lines_covered(node.args)
        except ValueError:
            start = end = node.lineno

        start = min(node.lineno, start)
        content = '\n'.join(self.lines[start - 1 : end])

        if not content.strip().endswith(':'):
            end += 1
            content = '\n'.join(self.lines[start - 1 : end])

        return left_align_block(content)

    def visit_ClassDef(self, node: ast.ClassDef) -> str:
        """convert a class into markdown"""
        md = [f'## class {self.get_qualified_name(node, node.name)}\n']
        doc = parse_google_docstring(ast.get_docstring(node))
        if doc['desc']:
            md.append(doc['desc'] + '\n')

        if doc['attributes']:
            md.append('**Attributes**\n')
            for attr in doc['attributes']:
                md.append(argument_md(**attr))
            md.append('')

        for elem in node.body:
            subnode = self.visit(elem)
            if subnode:
                md.append(subnode)
                md.append('')
        if self.hide_undoc and len(md) == 1:
            return ''
        return '\n'.join(md)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> str:
        """convert a function into markdown"""
        decorators = [self.visit(d) for d in node.decorator_list]
        args = []

        diff = len(node.args.args) - len(node.args.defaults)
        defaults = list(node.args.defaults)
        class_parent = isinstance(node.parent, ast.ClassDef)

        doc = parse_google_docstring(ast.get_docstring(node))

        class_doc = {}
        if class_parent and node.name == '__init__':
            class_doc = parse_google_docstring(ast.get_docstring(node.parent))

        if self.hide_private and node.name.startswith('_') and node.name != '__init__':
            return ''

        if not doc['desc'] and self.hide_undoc and not class_doc.get('desc', ''):
            return ''

        # mix the python built-in annotations with the docstring ones
        returns = {}
        if doc['returns']:
            returns = doc['returns'][0]
        parsed_return = self.visit(node.returns)
        if parsed_return:
            returns['type'] = parsed_return

        for index, arg in enumerate(node.args.args):
            defn = {'name': arg.arg}
            for doc_arg in class_doc.get('args', []) + doc['args']:
                if doc_arg['name'] == arg.arg:
                    defn.update(doc_arg)
            if index >= diff:
                defn['default'] = self.visit(defaults[index - diff])
            if arg.annotation:
                defn['type'] = self.visit(arg.annotation)

            args.append(defn)

        if (
            args
            and class_parent
            and 'property' not in decorators
            and 'staticmethod' not in decorators
        ):
            args = args[1:]

        args = [
            a for a in args if not self.hide_undoc_args or len([k for k in defn if defn[k]]) > 1
        ]
        heading_level = 3 if class_parent else 2
        name = self.get_qualified_name(node, node.name)

        if 'property' not in decorators:
            name += '()'

        return function_md(
            name,
            args,
            returns=returns,
            raises=doc['raises'],
            source_defn=self.get_function_def_segment(node),
            source=self.get_source_segment(node),
            note=doc['note'],
            desc=doc['desc'],
            heading_level=heading_level,
            examples=doc['example'],
        )

    def visit_Module(self, node: ast.Module) -> str:
        """
        Convert a module into markdown
        """
        classes = []
        functions = []
        constants = []
        node.name = self.name

        # register parents
        for subnode in ast.walk(node):
            for child in ast.iter_child_nodes(subnode):
                child.parent = subnode

        for elem in node.body:
            subnode = self.visit(elem)
            if not subnode:
                continue
            if isinstance(elem, ast.ClassDef):
                classes.append(subnode)
            elif isinstance(elem, ast.FunctionDef):
                functions.append(subnode)
            elif isinstance(elem, ast.Assign):
                constants.append(subnode)

        md = [f'# {self.name}\n']
        module_docstring = ast.get_docstring(node)

        if module_docstring:
            md.append(module_docstring)
            md.append('')

        for section in [constants, classes, functions]:
            if section:
                md.extend(section)
                md.append('')

        if not classes and not functions and not module_docstring and self.hide_undoc:
            return ''

        return '\n'.join(md)

    def visit_Name(self, node: ast.Name) -> str:
        return node.id

    def visit_NoneType(self, node: None) -> None:
        return node

    def visit_Subscript(self, node: ast.Subscript) -> str:
        inner = self.visit(node.slice.value)
        return f'{self.visit(node.value)}.<{inner}>'

    def visit_Assign(self, node: ast.Assign) -> str:
        expected_end_char = None

        if isinstance(node.value, ast.List):
            expected_end_char = ']'
        elif isinstance(node.value, ast.Call):
            expected_end_char = ')'

        md = []
        for target in node.targets:
            name = self.visit(target)
            source = left_align_block(self.get_source_segment(node, expected_end_char))

            md.extend(
                [f'## {self.get_qualified_name(node, name)}\n', f'```python\n{source}\n```\n']
            )
        return '\n'.join(md)

    def visit_Attribute(self, node: ast.Attribute) -> str:
        return self.visit(node.value)


def parse_module_file(
    filename: str,
    prefix: str = '',
    hide_private: bool = True,
    hide_undoc: bool = True,
    hide_undoc_args: bool = True,
    namespace_headers: bool = False,
) -> str:
    """
    convert a module into markdown

    Args:
        filename: the path to the file to be read
        prefix: the portion of the path that is not part of the package
        hide_private: hide privated functions, do not document (does not apply to __init__)
        hide_undoc: exclude undocumented functions (no docstring)
        hide_undoc_args: do not list arguments with neither type nor description

    Returns:
        the markdown string for this module
    """

    analyzer = ModuleAnalyzer(
        filename,
        prefix,
        hide_private=hide_private,
        hide_undoc=hide_undoc,
        hide_undoc_args=hide_undoc_args,
        namespace_headers=namespace_headers,
    )
    tree = ast.parse(analyzer.content)
    content = analyzer.visit(tree)
    return content


def extract_to_markdown(
    paths: List[str],
    output_dir: str,
    hide_private: bool = True,
    hide_undoc: bool = True,
    hide_undoc_args: bool = True,
    namespace_headers: bool = False,
):
    for path in paths:
        if path.endswith('/'):
            path = path[:-1]
        package = os.path.basename(path)
        prefix = path[0 : len(path) - len(package)]
        files = []
        if os.path.isfile(path):
            files.append(path)
        else:
            for root, dirs, walkfiles in os.walk(path):
                files.extend([os.path.join(root, w) for w in walkfiles if w.endswith('.py')])

        for filename in files:
            md = parse_module_file(
                filename,
                prefix,
                hide_private=hide_private,
                hide_undoc=hide_undoc,
                hide_undoc_args=hide_undoc_args,
                namespace_headers=namespace_headers,
            )
            if not md:
                continue
            module_file_output = os.path.join(
                output_dir, filename[len(prefix) :].replace('.py', '.md')
            )
            dirname = os.path.dirname(module_file_output)
            os.makedirs(dirname, exist_ok=True)

            print('writing:', module_file_output)
            with open(module_file_output, 'w') as fh:
                fh.write(md)


def command_interface():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--show_private',
        default=False,
        action='store_true',
        help='show private functions in output (__init__ is not considered private is is shown by default)',
    )
    parser.add_argument(
        '--show_undoc',
        default=False,
        action='store_true',
        help='show undocumented functions (no docstring)',
    )
    parser.add_argument(
        '--show_undoc_args',
        default=False,
        action='store_true',
        help='show/list function arguments with neither type nor description',
    )
    parser.add_argument('-o', '--output_dir', help='The output directory', required=True)
    parser.add_argument(
        'inputs', nargs='+', help='path(s) to python package directories to pull docstrings from'
    )
    parser.add_argument(
        '--namespace_headers',
        default=False,
        action='store_true',
        help='If true then the package/module prefix will be prepended to function/class names. Ex. pacakge_name.module_name.function_name instead of just function_name',
    )
    args = parser.parse_args()
    extract_to_markdown(
        args.inputs,
        args.output_dir,
        hide_private=not args.show_private,
        hide_undoc=not args.show_undoc,
        hide_undoc_args=not args.show_undoc_args,
        namespace_headers=args.namespace_headers,
    )
