import argparse
import ast
import os
from typing import Dict, List, Optional, Tuple

from .markdown import module_to_markdown
from .parsers import left_align_block, parse_google_docstring
from .types import (
    ParsedClass,
    ParsedDocstring,
    ParsedFunction,
    ParsedModule,
    ParsedParameter,
    ParsedReturn,
    ParsedVariable,
)


def get_by_name(name: str, list_to_search: List[Dict]) -> Optional[Dict]:
    for item in list_to_search:
        if item['name'] == name:
            return item
    return None


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

    def get_qualified_name(self, node: ast.AST, name: str) -> Optional[str]:
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

    def get_function_def_segment(self, node: ast.FunctionDef) -> str:
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

    def visit_ClassDef(self, node: ast.ClassDef) -> ParsedClass:
        """convert a class into markdown"""
        result = ParsedClass(
            {
                'name': self.get_qualified_name(node, node.name),
                'description': '',
                'attributes': [],
                'functions': [],
                'hidden': False,
            }
        )
        doc = parse_google_docstring(ast.get_docstring(node), self.hide_undoc_args)
        if doc and doc.get('description', ''):
            result['description'] = doc['description']

        if doc and doc['attributes']:
            result['attributes'] = doc['attributes']

        for elem in node.body:
            subnode = self.visit(elem)
            if subnode:
                result['functions'].append(subnode)
        if self.hide_undoc and not result['functions'] and not result['attributes']:
            result['hidden'] = True
        return result

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ParsedFunction:
        """convert a function into markdown"""

        decorators = {self.visit(d) for d in node.decorator_list}
        result = ParsedFunction(
            {
                'name': self.get_qualified_name(node, node.name),
                'hidden': False,
                'is_class_method': 'classmethod' in decorators,
                'is_static': 'staticmethod' in decorators,
                'is_getter': 'property' in decorators,
                'returns': ParsedReturn({}),
                'parameters': [],
                'raises': [],
                'examples': [],
                'description': '',
                'source_definition': self.get_function_def_segment(node),
                'source_code': self.get_source_segment(node),
            }
        )

        diff = len(node.args.args) - len(node.args.defaults)
        defaults = list(node.args.defaults)
        class_parent = isinstance(node.parent, ast.ClassDef)
        result['is_method'] = (
            class_parent
            and not result['is_static']
            and not result['is_getter']
            and not result['is_class_method']
        )

        doc = parse_google_docstring(ast.get_docstring(node), self.hide_undoc_args)
        result.update({d: doc[d] for d in doc if d != 'parameters'})

        class_doc = ParsedDocstring({})

        if class_parent and node.name == '__init__':
            class_doc = parse_google_docstring(ast.get_docstring(node.parent), self.hide_undoc_args)

        if self.hide_private and node.name.startswith('_') and node.name != '__init__':
            result['hidden'] = True

        if (
            not doc['description']
            and self.hide_undoc
            and (not class_doc or not class_doc['description'])
        ):
            result['hidden'] = True

        # mix the python built-in annotations with the docstring ones
        result['returns'].update(doc['returns'])
        parsed_return = self.visit(node.returns)
        if parsed_return:
            result['returns']['type'] = parsed_return

        for index, arg in enumerate(node.args.args):
            arg_name = arg.arg
            defn = ParsedParameter({'name': arg_name})

            if index == 0:
                if arg_name == 'self' and result['is_method']:
                    continue
                if arg_name == 'cls' and result['is_class_method']:
                    continue
            # update param from docstrings
            function_arg_doc = get_by_name(arg_name, doc.get('parameters', []))
            class_arg_doc = get_by_name(arg_name, class_doc.get('parameters', []))
            if class_arg_doc:
                defn.update(class_arg_doc)
            if function_arg_doc:
                defn.update(function_arg_doc)

            if index >= diff:
                defn['default_value'] = self.visit(defaults[index - diff])
            if arg.annotation:
                defn['type'] = self.visit(arg.annotation)

            result['parameters'].append(defn)

        return result

    def visit_Module(self, node: ast.Module) -> ParsedModule:
        """
        Convert a module into markdown
        """
        classes: List[ParsedClass] = []
        functions: List[ParsedFunction] = []
        constants: List[ParsedVariable] = []
        result = ParsedModule(
            {
                'name': self.name,
                'variables': constants,
                'functions': functions,
                'classes': classes,
                'hidden': False,
                'description': ast.get_docstring(node) or '',
            }
        )
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
                constants.extend(subnode)

        module_docstring = ast.get_docstring(node)
        if not classes and not functions and not module_docstring and self.hide_undoc:
            result['hidden'] = True

        return result

    def visit_Name(self, node: ast.Name) -> str:
        return node.id

    def visit_NoneType(self, node: None) -> None:
        return node

    def visit_Tuple(self, node: ast.Tuple) -> str:
        content = ', '.join([self.visit(e) for e in node.elts])
        return content

    def visit_Subscript(self, node: ast.Subscript) -> str:
        inner = self.visit(node.slice.value)
        return f'{self.visit(node.value)}[{inner}]'

    def visit_Assign(self, node: ast.Assign) -> List[ParsedVariable]:
        expected_end_char = None

        if isinstance(node.value, ast.List):
            expected_end_char = ']'
        elif isinstance(node.value, ast.Call):
            expected_end_char = ')'

        result: List[ParsedVariable] = []
        for target in node.targets:
            name = self.visit(target)
            result.append(
                ParsedVariable(
                    {
                        'name': self.visit(target),
                        'source_code': left_align_block(
                            self.get_source_segment(node, expected_end_char)
                        ),
                    }
                )
            )
        return result

    def visit_Attribute(self, node: ast.Attribute) -> str:
        name = self.visit(node.value)

        if node.attr:
            return f'{name}.{node.attr}'
        return name


def parse_module_file(
    filename: str,
    prefix: str = '',
    hide_private: bool = True,
    hide_undoc: bool = True,
    hide_undoc_args: bool = True,
    namespace_headers: bool = False,
) -> ParsedModule:
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
                fh.write(module_to_markdown(md))


def command_interface() -> None:
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
