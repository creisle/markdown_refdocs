import re
from typing import Dict


def left_align_block(block):
    lines = block.split('\n')
    if not lines:
        return block

    indent = re.match(r'(\s*).*', lines[0]).group(1)
    content = '\n'.join([l[len(indent) :] for l in lines])
    return content


def parse_google_docstring(docstring: str) -> Dict:
    """
    parses a google-style docsting into a dictionary of the various sections
    """
    state = None
    tags = ['args', 'returns', 'raises', 'note', 'desc', 'example', 'attributes']
    content = {k: [] for k in tags}

    if not docstring:
        return content
    docstring = docstring.strip()

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

    for tag in ['attributes', 'args']:
        parsed_args = []
        for i, arg in enumerate(content[tag]):
            try:
                name, _, arg_type, arg_desc = re.match(
                    r'^(\w+)(\s+\(([^)]+)\))?:\s*(.*)$', arg
                ).groups()
                parsed_args.append({'name': name, 'type': arg_type, 'desc': arg_desc})
            except AttributeError:
                pass
        content[tag] = parsed_args

    for sec in ['returns', 'raises']:
        for i, line in enumerate(content[sec]):
            _, arg_type, arg_desc = re.match(r'^(([^:]+):)?\s*(.*)$', line).groups()
            content[sec][i] = {'type': arg_type, 'desc': arg_desc}

    content['desc'] = '\n'.join(content['desc'])
    content['note'] = '\n'.join(content['note'])

    for i, example in enumerate(content['example']):
        content['example'][i] = left_align_block('\n'.join(example))

    return content
