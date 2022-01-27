from typing import List

try:
    from typing import TypedDict  # type: ignore
except ImportError:
    from typing_extensions import TypedDict

Parsed: TypedDict = TypedDict(
    'Parsed', {'name': str, 'source_code': str, 'hidden': bool}, total=False
)


class ParsedParameter(Parsed, total=False):
    default_value: str
    type: str
    description: str


class ParsedReturn(TypedDict, total=False):
    type: str
    description: str


class ParsedFunction(Parsed, total=False):
    """
    Result of the combination of parsing the source code and combining with the docstring of a function
    """

    parameters: List[ParsedParameter]
    returns: ParsedReturn
    note: str
    raises: List[str]
    examples: List[str]
    description: str
    is_static: bool
    is_method: bool
    is_class_method: bool
    is_getter: bool


class ParsedDocstring(TypedDict, total=False):
    description: str
    note: str
    examples: List[str]
    raises: List[str]
    returns: ParsedReturn
    parameters: List[ParsedParameter]
    attributes: List[ParsedParameter]
    todo: List[str]


class ParsedVariable(Parsed, total=False):
    type: str
    description: str
    value: str
    attributes: List[Parsed]


class ParsedClass(Parsed, total=False):
    functions: List[ParsedFunction]
    variables: List[ParsedVariable]
    description: str
    inherits: List[str]
    attributes: List[Parsed]


class ParsedModule(Parsed, total=False):
    classes: List[ParsedClass]
    functions: List[ParsedFunction]
    variables: List[ParsedVariable]
    description: str


ADMONITIONS = [
    'warning',
    'note',
    'info',
    'bug',
    'tip',
    'question',
    'failure',
    'danger',
    'quote',
    'todo',
]
