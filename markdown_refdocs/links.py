import os
import re
from typing import Dict, Optional

from .types import ParsedModule


def create_types_mapping(modules: Dict[str, ParsedModule]) -> Dict[str, str]:
    """
    Creates mapping of type name to links

    Note:
        This only links within a package
    """
    simple_mapping: Dict[str, Optional[str]] = {}
    qualified_mapping: Dict[str, Optional[str]] = {}

    def add_to_mappings(module: ParsedModule, short_name: str, prefix: str = 'class-'):
        qualified_name = f'{module["name"]}.{short_name}'
        url = f'./{path}/#{prefix}{short_name.lower()}'

        if short_name in simple_mapping:
            simple_mapping[short_name] = None  # drop name clashes
        else:
            simple_mapping[short_name] = url

        if qualified_name in qualified_mapping:
            qualified_mapping[qualified_name] = None  # drop name clashes
        else:
            qualified_mapping[qualified_name] = url

    for path, module in modules.items():
        for var in module.get('variables', []):
            if re.match(r'^[A-Z][a-z]', var['name']):
                add_to_mappings(module, var['name'], '')

        for cls in module.get('classes', []):
            add_to_mappings(module, cls['name'])

    simple_mapping.update(qualified_mapping)
    return {k: v for (k, v) in simple_mapping.items() if v is not None}


def create_relative_types_mapping(current_file: str, types_mapping: Dict[str, str]):
    relative_mapping: Dict[str, str] = {}

    for linked_type, path_link in types_mapping.items():
        original_path, hash_location = path_link.split('#')
        relative_path = re.sub(
            r'\.md$', '', os.path.join(os.path.relpath(original_path, current_file))
        )
        if relative_path == '.':
            relative_mapping[linked_type] = f'#{hash_location}'
        else:
            relative_mapping[linked_type] = f'{relative_path}/#{hash_location}'
    return relative_mapping
