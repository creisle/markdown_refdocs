import re
from typing import Any, Dict

from .types import ParsedDocstring, ParsedParameter, ParsedReturn


def left_align_block(block: str) -> str:
    lines = block.split('\n')
    if not lines:
        return block

    indent = re.match(r'(\s*).*', lines[0]).group(1)
    content = '\n'.join([line[len(indent) :] for line in lines])
    return content


def parse_google_docstring(docstring: str, hide_undoc: bool = True) -> ParsedDocstring:
    """
    parses a google-style docsting into a dictionary of the various sections
    """
    state = None
    tags = ['args', 'returns', 'raises', 'note', 'desc', 'example', 'attributes']
    content: Dict[str, Any] = {tag: [] for tag in tags}

    docstring = (docstring if docstring else '').strip()

    # start with the description
    for line in docstring.split('\n'):
        line = line.strip()
        new_state = line.lower().replace(':', '') if line.endswith(':') else ''

        if new_state in tags:
            state = new_state
            if state == 'example':
                content[state].append([])
            continue

        if state is None:
            # no elements yet
            if not line:
                continue
            else:
                state = 'desc'
                content['desc'] = [line]
                continue

        if not line:
            state = ''
            continue

        if state == 'example':
            content[state][-1].append(line)
        elif state in tags:
            content[state].append(line)

    result = ParsedDocstring(
        {
            'raises': [],
            'attributes': [],
            'parameters': [],
            'description': '',
            'returns': ParsedReturn({}),
            'examples': [],
        }
    )

    for tag in ['attributes', 'args']:
        parsed_args = []
        for i, arg in enumerate(content[tag]):
            try:
                name, _, arg_type, arg_desc = re.match(
                    r'^(\w+)(\s+\(([^)]+)\))?:\s*(.*)$', arg
                ).groups()
                parsed_args.append(
                    ParsedParameter(
                        {
                            'name': name,
                            'type': arg_type,
                            'description': arg_desc,
                            'hidden': not arg_desc and hide_undoc,
                        }
                    )
                )
            except AttributeError:
                pass

        if tag == 'args':
            result['parameters'] = parsed_args
        else:
            result[tag] = parsed_args

    for i, line in enumerate(content['raises']):
        _, arg_type, arg_desc = re.match(r'^(([^:]+):)?\s*(.*)$', line).groups()
        result['raises'].append(ParsedReturn({'type': arg_type, 'description': arg_desc}))

    for i, line in enumerate(content['returns']):
        _, arg_type, arg_desc = re.match(r'^(([^:]+):)?\s*(.*)$', line).groups()
        if result['returns']:
            raise AttributeError('unable to parse docstring with multiple returns')
        result['returns'] = ParsedReturn({'type': arg_type, 'description': arg_desc})

    result['description'] = '\n'.join(content['desc'])
    result['note'] = '\n'.join(content['note'])

    for i, example in enumerate(content['example']):
        result['examples'].append(left_align_block('\n'.join(example)))

    return result
