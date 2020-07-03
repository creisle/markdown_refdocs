import os
import sys
from unittest.mock import mock_open, patch

from markdown_refdocs.main import command_interface, parse_module_file
from markdown_refdocs.markdown import module_to_markdown
from markdown_refdocs.types import ParsedVariable


class TestParseModuleFile:
    def test_multiple_decorators(self):
        data = """
from pyramid.view import (
    view_config,
)
from pyramid.security import (
    NO_PERMISSION_REQUIRED
)

@view_config(route_name='swagger', renderer='lims:templates/swagger.mak', permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='swagger.json', renderer='json', permission=NO_PERMISSION_REQUIRED)
def swagger(request):
    '''I am a docstring'''
    pass
"""
        expected = """
# simple_module

## swagger()

I am a docstring

```python
@view_config(route_name='swagger', renderer='lims:templates/swagger.mak', permission=NO_PERMISSION_REQUIRED)
@view_config(route_name='swagger.json', renderer='json', permission=NO_PERMISSION_REQUIRED)
def swagger(request):
```

**Args**

- request
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_simple_module(self):
        data = """
def simple_function(arg1: str, arg2: int):
    '''
    this function does stuff
    '''
    pass
"""
        expected = """# simple_module

## simple\\_function()

this function does stuff

```python
def simple_function(arg1: str, arg2: int):
```

**Args**

- arg1 (`str`)
- arg2 (`int`)
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_overwrite_docstring_with_annotations(self):
        data = """
def simple_function(arg1: str, arg2: int):
    '''
    this function does stuff

    Args:
        arg1 (int): this is the first argument
    '''
    pass
"""
        expected = """# simple_module

## simple\\_function()

this function does stuff

```python
def simple_function(arg1: str, arg2: int):
```

**Args**

- arg1 (`str`): this is the first argument
- arg2 (`int`)
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_examples_from_docstring(self):
        data = """
def simple_function(arg1: str, arg2: int):
    '''
    this function does stuff

    Args:
        arg1 (int): this is the first argument

    Example:
        >>> simple_function('1', 2)
        'something'
    '''
    pass
"""
        expected = """# simple_module

## simple\\_function()

this function does stuff

```python
def simple_function(arg1: str, arg2: int):
```

**Args**

- arg1 (`str`): this is the first argument
- arg2 (`int`)

**Examples**

```python
>>> simple_function('1', 2)
'something'
```
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_returns_from_type_annotation(self):
        data = """
def simple_function(arg1: str, arg2: int) -> str:
    '''
    this function does stuff

    Args:
        arg1 (int): this is the first argument
    '''
    pass
"""
        expected = """# simple_module

## simple\\_function()

this function does stuff

```python
def simple_function(arg1: str, arg2: int) -> str:
```

**Args**

- arg1 (`str`): this is the first argument
- arg2 (`int`)

**Returns**

- `str`
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_parses_raise(self):
        data = """
def simple_function(arg1: str, arg2: int):
    '''
    this function does stuff

    Args:
        arg1 (int): this is the first argument

    Raises:
        NotImplementedError: stuff
    '''
    pass
"""
        expected = """# simple_module

## simple\\_function()

this function does stuff

```python
def simple_function(arg1: str, arg2: int):
```

**Args**

- arg1 (`str`): this is the first argument
- arg2 (`int`)

**Raises**

- `NotImplementedError`: stuff
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_multiline_function_def(self):
        data = """
def simple_function(
    arg1: str,
    arg2: int,
):
    '''
    this function does stuff

    Args:
        arg1 (int): this is the first argument
    '''
    pass
"""
        expected = """# simple_module

## simple\\_function()

this function does stuff

```python
def simple_function(
    arg1: str,
    arg2: int,
):
```

**Args**

- arg1 (`str`): this is the first argument
- arg2 (`int`)
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_class_desc(self):
        data = """
class SomeClass:
    '''
    say something

    Attributes:
        attr1 (int): an thing on a class instance
    '''
    pass
"""
        expected_md = """# simple_module

## class SomeClass

say something

**Attributes**

- attr1 (`int`): an thing on a class instance
"""
        expected_parse = {
            'name': 'simple_module',
            'hidden': False,
            'functions': [],
            'description': '',
            'variables': [],
            'classes': [
                {
                    'name': 'SomeClass',
                    'description': 'say something',
                    'inherits': [],
                    'hidden': False,
                    'functions': [],
                    'examples': [],
                    'attributes': [
                        {
                            'hidden': False,
                            'name': 'attr1',
                            'type': 'int',
                            'description': 'an thing on a class instance',
                        }
                    ],
                }
            ],
        }
        with patch('builtins.open', mock_open(read_data=data)):
            parsed = parse_module_file('simple_module.py', '')
            assert parsed == expected_parse
            md = module_to_markdown(parsed)
            assert md.strip() == expected_md.strip()

    def test_class_methods(self):
        data = """
class SomeClass:
    def some_method_on_a_class(self):
        '''
        I am a method
        '''
        pass
"""
        expected = """# simple_module

## class SomeClass

### SomeClass.some\\_method\\_on\\_a\\_class()

I am a method

```python
def some_method_on_a_class(self):
```
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_pass_class_args_to_construcor(self):
        data = """
class SomeClass:
    '''
    Args:
        arg1: I am in the wrong place but can be moved
    '''
    def __init__(self, arg1):
        '''
        I am a method
        '''
        pass
"""
        expected = """# simple_module

## class SomeClass

### SomeClass.\\_\\_init\\_\\_()

I am a method

```python
def __init__(self, arg1):
```

**Args**

- arg1: I am in the wrong place but can be moved
"""
        with patch('builtins.open', mock_open(read_data=data)):

            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_module_constant(self):
        data = """
CONSTANT_THING = 'some constant thing'
"""
        expected = """# simple_module

## CONSTANT_THING

```python
CONSTANT_THING = 'some constant thing'
```
"""
        with patch('builtins.open', mock_open(read_data=data)):

            md = module_to_markdown(parse_module_file('simple_module.py', '', hide_undoc=False))
            assert md.strip() == expected.strip()

    def test_module_constant_pulled_when_any_docstring(self):
        data = """
'''
this is a docstring for the module
'''

CONSTANT_THING = 'some constant thing'
"""
        expected = """# simple_module

this is a docstring for the module

## CONSTANT_THING

```python
CONSTANT_THING = 'some constant thing'
```
"""
        with patch('builtins.open', mock_open(read_data=data)):

            md = module_to_markdown(parse_module_file('simple_module.py', ''))
            assert md.strip() == expected.strip()

    def test_nested_return_type_annotation(self):
        data = """
def some_function() -> List[Dict]:
    pass
"""
        expected = """# simple_module

## some\\_function()

```python
def some_function() -> List[Dict]:
```

**Returns**

- `List[Dict]`
"""
        with patch('builtins.open', mock_open(read_data=data)):

            md = module_to_markdown(parse_module_file('simple_module.py', '', hide_undoc=False))
            assert md.strip() == expected.strip()

    def test_multiline_module_constant(self):
        data = """
CONSTANT_THING = [
    'some',
    'constant thing'
]
"""
        expected = """# simple_module

## CONSTANT_THING

```python
CONSTANT_THING = [
    'some',
    'constant thing'
]
```
"""
        with patch('builtins.open', mock_open(read_data=data)):

            md = module_to_markdown(parse_module_file('simple_module.py', '', hide_undoc=False))
            assert md.strip() == expected.strip()

    def test_complex_types(self):
        data = """
from typing import List, Dict, Tuple

def some_function() -> Tuple[List, Dict[str,int]]:
    pass
"""
        expected = """# simple_module

## some\\_function()

```python
def some_function() -> Tuple[List, Dict[str,int]]:
```

**Returns**

- `Tuple[List, Dict[str, int]]`
"""
        with patch('builtins.open', mock_open(read_data=data)):

            md = module_to_markdown(parse_module_file('simple_module.py', '', hide_undoc=False))
            assert md.strip() == expected.strip()

    def test_namespaced_types(self):
        data = """
from typing import List, Dict, Tuple
import ast

def some_function(arg1: ast.AST):
    pass
"""
        expected = """# simple_module

## some\\_function()

```python
def some_function(arg1: ast.AST):
```

**Args**

- arg1 (`ast.AST`)
"""
        with patch('builtins.open', mock_open(read_data=data)):

            md = module_to_markdown(parse_module_file('simple_module.py', '', hide_undoc=False))
            assert md.strip() == expected.strip()

    def test_callable(self):
        data = """
class ResourceFieldDef(_ResourceFieldDefReq, total=False):
    update: Callable[[Any, Union[int, str]], None]
    deprecated: bool
"""
        expected = """# simple_module

## class ResourceFieldDef

**inherits** `_ResourceFieldDefReq`

**Attributes**

- update (`Callable[[Any, Union[int, str]], None]`)
- deprecated (`bool`)
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = module_to_markdown(parse_module_file('simple_module.py', '', hide_undoc=False))
            assert md.strip() == expected.strip()

    def test_typed_dict(self):
        data = """
from typings import TypedDict

class SomeType(TypedDict):
    name: str
    parent: str
    grandparent: str
"""
        expected = """# simple_module

## class SomeType

**inherits** `TypedDict`

**Attributes**

- name (`str`)
- parent (`str`)
- grandparent (`str`)
"""
        expect_parsed = {
            'name': 'simple_module',
            'hidden': False,
            'variables': [],
            'functions': [],
            'description': '',
            'classes': [
                {
                    'name': 'SomeType',
                    'inherits': ['TypedDict'],
                    'description': '',
                    'hidden': False,
                    'examples': [],
                    'attributes': [
                        {'name': 'name', 'type': 'str', 'source_code': 'name: str'},
                        {'name': 'parent', 'type': 'str', 'source_code': 'parent: str'},
                        {'name': 'grandparent', 'type': 'str', 'source_code': 'grandparent: str',},
                    ],
                    'functions': [],
                }
            ],
        }

        with patch('builtins.open', mock_open(read_data=data)):
            parsed = parse_module_file('simple_module.py', '', hide_undoc=False)
            assert parsed == expect_parsed
            md = module_to_markdown(parsed)
            assert md.strip() == expected.strip()

    def test_typed_dict_with_docstring(self):
        data = """
from typings import TypedDict

class SomeType(TypedDict):
    '''
    Attributes:
        parent: the name of the parent
    '''
    name: str
    parent: str
    grandparent: str
"""
        expected = """# simple_module

## class SomeType

**inherits** `TypedDict`

**Attributes**

- name (`str`)
- parent (`str`): the name of the parent
- grandparent (`str`)
"""
        expect_parsed = {
            'name': 'simple_module',
            'hidden': False,
            'variables': [],
            'functions': [],
            'description': '',
            'classes': [
                {
                    'name': 'SomeType',
                    'description': '',
                    'inherits': ['TypedDict'],
                    'examples': [],
                    'hidden': False,
                    'functions': [],
                    'attributes': [
                        {'name': 'name', 'type': 'str', 'source_code': 'name: str'},
                        {
                            'name': 'parent',
                            'type': 'str',
                            'source_code': 'parent: str',
                            'description': 'the name of the parent',
                            'hidden': False,
                        },
                        {'name': 'grandparent', 'type': 'str', 'source_code': 'grandparent: str'},
                    ],
                }
            ],
        }

        with patch('builtins.open', mock_open(read_data=data)):
            parsed = parse_module_file('simple_module.py', '', hide_undoc=False)
            assert parsed == expect_parsed
            md = module_to_markdown(parsed)
            assert md.strip() == expected.strip()

    def test_alternate_typeddict_notation(self):
        data = """try:
    from typing import TypedDict  # type: ignore
except ImportError:
    from typing_extensions import TypedDict

Parsed: TypedDict = TypedDict('Parsed', {'name': str, 'source_code': str, 'hidden': bool})"""
        expect_parsed = [
            ParsedVariable(
                {
                    'type': 'TypedDict',
                    'name': 'Parsed',
                    'source_code': """Parsed: TypedDict = TypedDict('Parsed', {'name': str, 'source_code': str, 'hidden': bool})""",
                    'attributes': [
                        {'name': 'name', 'type': 'str'},
                        {'name': 'source_code', 'type': 'str'},
                        {'name': 'hidden', 'type': 'bool'},
                    ],
                }
            )
        ]

        with patch('builtins.open', mock_open(read_data=data)):
            parsed = parse_module_file('simple_module.py', '', hide_undoc=False)
            assert parsed['variables'] == expect_parsed

    def test_multiline_docstring_desc(self):
        data = """
def prefix_split(text):
    '''
    Split the input text into a prefix and suffix, according to the following patterns:

    If the input string is letters followed by numbers, return them separately in a tuple.
    If the input string is only letters, return a tuple of ({letters}, None).
    If the input string is only numbers, return a tuple of (None, {numbers}).

    Otherwise return a tuple of Nones.

    Args:
        text (str): the input to split.
    '''
    pass
"""
        expected = """# simple_module

## prefix\\_split()

Split the input text into a prefix and suffix, according to the following patterns:

If the input string is letters followed by numbers, return them separately in a tuple.
If the input string is only letters, return a tuple of ({letters}, None).
If the input string is only numbers, return a tuple of (None, {numbers}).

Otherwise return a tuple of Nones.

```python
def prefix_split(text):
```

**Args**

- text (`str`): the input to split.
"""
        with patch('builtins.open', mock_open(read_data=data)):
            parsed = parse_module_file('simple_module.py', '', hide_undoc=False)
            md = module_to_markdown(parsed)
            assert md.strip() == expected.strip()


class TestCommandInterface:
    def test_package_path(self, tmpdir):
        path = os.path.join(os.path.dirname(__file__), '../markdown_refdocs')
        with patch.object(
            sys,
            'argv',
            ['', path, '-o', tmpdir.dirname, '--show_undoc', '--show_undoc_args', '--show_private'],
        ):
            command_interface()

        modules = [
            os.path.join(tmpdir.dirname, 'markdown_refdocs', f'{m}.md')
            for m in ['main', 'markdown', 'parsers', '__init__']
        ]

        for module in modules:
            assert os.path.exists(module)
