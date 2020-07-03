import re
from typing import Any, Dict

from .types import ParsedDocstring, ParsedParameter, ParsedReturn, ADMONITIONS


def left_align_block(block: str) -> str:
    lines = block.split('\n')
    if not lines:
        return block

    indent = re.match(r'(\s*).*', lines[0]).group(1)  # type: ignore
    content = '\n'.join([line[len(indent) :] for line in lines])
    return content


def parse_google_docstring(
    docstring: str, hide_undoc: bool = True, function_name=''
) -> ParsedDocstring:
    """
    parses a google-style docsting into a dictionary of the various sections
    """
    state = None
    tags = ['args', 'returns', 'raises', 'note', 'desc', 'example', 'attributes', 'warning']
    content: Dict[str, Any] = {tag: [] for tag in tags}

    docstring = (docstring if docstring else '').strip()

    # start with the description
    for line in docstring.split('\n'):
        line = line.strip()
        if not line and state is None:
            continue
        new_state = line.lower().replace(':', '') if line.endswith(':') else ''

        if new_state in tags:
            state = new_state
            if state == 'example':
                content[state].append([])
            continue

        if state is None:
            # no elements yet
            state = 'desc'
            content['desc'] = [line]
        elif state == 'desc':
            content['desc'].append(line)
        elif line:
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
                name, _, arg_type, arg_desc = re.match(  # type: ignore
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
        _, arg_type, arg_desc = re.match(r'^(([^:]+):)?\s*(.*)$', line).groups()  # type: ignore
        result['raises'].append(ParsedReturn({'type': arg_type, 'description': arg_desc}))

    for i, line in enumerate(content['returns']):
        _, arg_type, arg_desc = re.match(r'^(([^:]+):)?\s*(.*)$', line).groups()  # type: ignore
        if result['returns']:
            result['returns']['description'] += ' ' + line
        else:
            print(
                f'warning: {function_name} multiple return lines, being appended to the description'
            )
            result['returns'] = ParsedReturn({'type': arg_type, 'description': arg_desc})

    result['description'] = '\n'.join(content['desc']).strip()

    for i, example in enumerate(content['example']):
        result['examples'].append(left_align_block('\n'.join(example)))

    for admon in ADMONITIONS:
        if content.get(admon, []):
            result[admon] = content[admon]

    return result
