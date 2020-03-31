import sys
import os
from unittest.mock import patch, mock_open

from markdown_refdocs.main import parse_module_file, command_interface


class TestParseModuleFile:
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
            md = parse_module_file('simple_module.py', '')
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
            md = parse_module_file('simple_module.py', '')
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
            md = parse_module_file('simple_module.py', '')
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
            md = parse_module_file('simple_module.py', '')
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
            md = parse_module_file('simple_module.py', '')
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
            md = parse_module_file('simple_module.py', '')
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
        expected = """# simple_module

## class SomeClass

say something

**Attributes**

- attr1 (`int`): an thing on a class instance
"""
        with patch('builtins.open', mock_open(read_data=data)):
            md = parse_module_file('simple_module.py', '')
            assert md.strip() == expected.strip()

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
            md = parse_module_file('simple_module.py', '')
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

            md = parse_module_file('simple_module.py', '')
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

            md = parse_module_file('simple_module.py', '', hide_undoc=False)
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

            md = parse_module_file('simple_module.py', '')
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

- `List.<Dict>`
"""
        with patch('builtins.open', mock_open(read_data=data)):

            md = parse_module_file('simple_module.py', '', hide_undoc=False)
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

            md = parse_module_file('simple_module.py', '', hide_undoc=False)
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
