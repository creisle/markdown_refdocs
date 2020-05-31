import re
from itertools import permutations
from typing import Dict, Tuple

from .types import ParsedClass, ParsedFunction, ParsedModule, ParsedVariable


def _create_type_link(type_name: str, types_links: Dict[str, str] = {}) -> Tuple[str, bool]:
    m = re.match(r'^Optional\[(.*)\]$', type_name)
    if m:
        inner_link, contains_link = _create_type_link(m.group(1), types_links)
        if contains_link:
            return f'Optional\\[{inner_link}\\]', True
    if type_name in types_links:
        return f'[{type_name}]({types_links[type_name]})', True

    for typing_type in ['Dict', 'List', 'Iterable', 'Set', 'Optional']:
        for link_type in types_links:
            if f'{typing_type}[{link_type}]' == type_name:
                inner_link, contains_link = _create_type_link(link_type, types_links)
                if contains_link:
                    return f'{typing_type}\\[{inner_link}\\]', True

    for typing_type in ['str', 'Tuple', 'int']:
        for link_type in types_links:
            if f'Dict[{typing_type}, {link_type}]' == type_name:
                inner_link, contains_link = _create_type_link(link_type, types_links)
                if contains_link:
                    return f'Dict\\[`{typing_type}`, {inner_link}\\]', True

    for typing_type in ['Union', 'Tuple']:
        for first, second in permutations(types_links.keys(), 2):
            double_link = f'{typing_type}[{first}, {second}]'
            if double_link == type_name:
                first_link, contains_link = _create_type_link(first, types_links)
                second_link, contains_other_link = _create_type_link(second, types_links)
                if contains_link or contains_other_link:
                    return f'{typing_type}\\[{first_link}, {second_link}\\]', True

    return type_name, False


def create_type_link(type_name: str, types_links: Dict[str, str] = {}) -> str:
    type_link, has_link = _create_type_link(type_name, types_links)
    if not has_link:
        return f'`{type_link}`'
    return type_link


def argument_md(
    name: str = '',
    type: str = None,
    description: str = '',
    default_value: str = None,
    hidden: bool = False,
    types_links: Dict[str, str] = {},
    **kwargs,
) -> str:
    md = ''
    if hidden:
        return ''
    if type:
        type = create_type_link(type, types_links)

    if type and not name:
        md = f'- {type}'
    elif name:
        md = f'- {name}'
        if type:
            md = f'- {name} ({type})'

    if description:
        md += f': {description}'
    return md


def function_to_markdown(
    parsed: ParsedFunction, heading_level: int = 2, types_links: Dict[str, str] = {}
) -> str:
    """
    Generate a markdown string for a function definition
    """
    if parsed.get('hidden', False):
        return ''
    heading = '#' * heading_level
    name = parsed['name'].replace('_', '\\_')
    md = [f'{heading} {name}()\n']
    if parsed.get('description', ''):
        md.extend([parsed['description'], ''])
    if parsed.get('source_definition', ''):
        md.append(f'```python\n{parsed["source_definition"]}\n```\n')

    if parsed.get('parameters', ''):
        md.append('**Args**\n')
        for arg in parsed['parameters']:
            md.append(argument_md(types_links=types_links, **arg))
        md.append('')

    if parsed.get('returns', ''):
        md.append('**Returns**\n')
        md.append(argument_md(types_links=types_links, **parsed['returns']))
        md.append('')

    if parsed.get('raises', ''):
        md.append('**Raises**\n')
        for arg in parsed['raises']:
            md.append(argument_md(types_links=types_links, **arg))
        md.append('')

    if parsed.get('examples', ''):
        md.append('**Examples**\n')
        for example in parsed['examples']:
            md.append(f'```python\n{example}\n```\n')
        md.append('')

    return '\n'.join(md)


def class_to_markdown(parsed: ParsedClass, types_links: Dict[str, str] = {}) -> str:
    if parsed.get('hidden', False):
        return ''
    md = [f'## class {parsed["name"]}', '']
    if parsed.get('inherits', False):
        md.extend(
            [
                '**inherits** '
                + ' '.join([create_type_link(t, types_links) for t in parsed['inherits']]),
                '',
            ]
        )

    if parsed.get('description', ''):
        md.extend([parsed['description'], ''])

    if parsed.get('attributes', ''):
        md.append('**Attributes**\n')
        for attr in parsed['attributes']:
            md.append(argument_md(types_links=types_links, **attr))
        md.append('')

    if parsed.get('functions', ''):
        for func in parsed['functions']:
            md.append(function_to_markdown(func, heading_level=3, types_links=types_links))
        md.append('')
    return '\n'.join(md)


def constant_to_markdown(parsed: ParsedVariable, types_links: Dict[str, str] = {}) -> str:
    md = [f'## {parsed["name"]}', '']
    if parsed['source_code']:
        md.append(f'```python\n{parsed["source_code"]}\n```\n')

    if parsed.get('attributes', ''):
        md.append('**Attributes**\n')
        for attr in parsed['attributes']:
            md.append(argument_md(types_links=types_links, **attr))
        md.append('')

    return '\n'.join(md)


def module_to_markdown(parsed: ParsedModule, types_links: Dict[str, str] = {}) -> str:
    if parsed.get('hidden', False):
        return ''
    md = [f'# {parsed["name"]}\n']

    if parsed['description']:
        md.extend([parsed['description'], ''])

    if parsed['variables']:
        for variable in parsed['variables']:
            md.append(constant_to_markdown(variable, types_links=types_links))

    for cls in parsed['classes']:
        md.append(class_to_markdown(cls, types_links=types_links))

    for func in parsed['functions']:
        md.append(function_to_markdown(func, types_links=types_links))

    return '\n'.join(md)
