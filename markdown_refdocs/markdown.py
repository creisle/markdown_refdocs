from .types import ParsedClass, ParsedFunction, ParsedModule, ParsedVariable


def argument_md(
    name: str = '',
    type: str = None,
    description: str = '',
    default_value: str = None,
    hidden: bool = False,
) -> str:
    md = ''
    if hidden:
        return ''
    if type and not name:
        md = f'- `{type}`'
    elif name:
        md = f'- {name}'
        if type:
            md = f'- {name} (`{type}`)'

    if description:
        md += f': {description}'
    return md


def function_to_markdown(parsed: ParsedFunction, heading_level: int = 2) -> str:
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
            md.append(argument_md(**arg))
        md.append('')

    if parsed.get('returns', ''):
        md.append('**Returns**\n')
        md.append(argument_md(**parsed['returns']))
        md.append('')

    if parsed.get('raises', ''):
        md.append('**Raises**\n')
        for arg in parsed['raises']:
            md.append(argument_md(**arg))
        md.append('')

    if parsed.get('examples', ''):
        md.append('**Examples**\n')
        for example in parsed['examples']:
            md.append(f'```python\n{example}\n```\n')
        md.append('')

    return '\n'.join(md)


def class_to_markdown(parsed: ParsedClass) -> str:
    if parsed.get('hidden', False):
        return ''
    md = [f'## class {parsed["name"]}\n']
    if parsed.get('description', ''):
        md.extend([parsed['description'], ''])

    if parsed.get('attributes', ''):
        md.append('**Attributes**\n')
        for attr in parsed['attributes']:
            md.append(argument_md(**attr))
        md.append('')

    if parsed.get('functions', ''):
        for func in parsed['functions']:
            md.append(function_to_markdown(func, heading_level=3))
        md.append('')
    return '\n'.join(md)


def constant_to_markdown(parsed: ParsedVariable) -> str:
    md = [f'## {parsed["name"]}', '']
    if parsed['source_code']:
        md.append(f'```python\n{parsed["source_code"]}\n```\n')
    return '\n'.join(md)


def module_to_markdown(parsed: ParsedModule) -> str:
    if parsed.get('hidden', False):
        return ''
    md = [f'# {parsed["name"]}\n']

    if parsed['description']:
        md.extend([parsed['description'], ''])

    if parsed['variables']:
        for variable in parsed['variables']:
            md.append(constant_to_markdown(variable))

    for cls in parsed['classes']:
        md.append(class_to_markdown(cls))

    for func in parsed['functions']:
        md.append(function_to_markdown(func))

    return '\n'.join(md)
