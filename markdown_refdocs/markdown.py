import re
from typing import Dict, List

from .types import ParsedClass, ParsedFunction, ParsedModule, ParsedVariable, ADMONITIONS


def create_type_link(type_name: str, types_links: Dict[str, str] = {}) -> str:
    tokens = re.split(r'(\[|\]|\s|,)', str(type_name))

    linked = []
    contains_link = False
    for token in tokens:
        if token in types_links:
            contains_link = True
            linked.append(f'[{token}]({types_links[token]})')
        elif token in ['str', 'int', 'bool', 'float']:
            linked.append(f'`{token}`')
        elif token in [']', '[']:
            linked.append(f'\\{token}')
        else:
            linked.append(token)

    if not contains_link:
        return f'`{type_name}`'
    return ''.join(linked)


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


def admonitions_to_markdown(parsed: Dict[str, List[str]]) -> str:
    md: List[str] = []
    for admonition in ADMONITIONS:
        if parsed.get(admonition, []):
            md.append(f'!!! {admonition}')
            for line in parsed[admonition]:
                md.append(f'\t{line}')
            md.append('')
    return '\n'.join(md)


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

    admon_md = admonitions_to_markdown(parsed)
    if admon_md:
        md.append(admon_md)

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

    admon_md = admonitions_to_markdown(parsed)
    if admon_md:
        md.append(admon_md)

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
