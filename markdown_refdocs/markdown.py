from typing import List, Dict


def argument_md(name: str = '', type: str = None, desc: str = '', default: str = None) -> str:
    md = ''
    if type and not name:
        md = f'- `{type}`'
    elif name:
        md = f'- {name}'
        if type:
            md = f'- {name} (`{type}`)'

    if desc:
        md += f': {desc}'
    return md


def function_md(
    name: str,
    args: List[Dict] = [],
    returns: Dict = {},
    raises: List[Dict] = [],
    source_defn: str = '',
    source: str = '',
    heading_level: int = 3,
    desc: str = '',
    note: str = '',
    examples: List[str] = [],
) -> str:
    """
    Generate a markdown string for a function definition
    """
    heading = '#' * heading_level
    name = name.replace('_', '\\_')
    md = [f'{heading} {name}\n']
    if desc:
        md.extend([desc, ''])
    md.append(f'```python\n{source_defn}\n```\n')

    if args:
        md.append('**Args**\n')
        for arg in args:
            md.append(argument_md(**arg))
        md.append('')

    if returns:
        md.append('**Returns**\n')
        md.append(argument_md(**returns))
        md.append('')

    if raises:
        md.append('**Raises**\n')
        for arg in raises:
            md.append(argument_md(**arg))
        md.append('')

    if examples:
        md.append(f'**Examples**\n')
        for example in examples:
            md.append(f'```python\n{example}\n```\n')
        md.append('')

    return '\n'.join(md)
