from typing import List

try:
    from typing import TypedDict  # type: ignore
except ImportError:
    from typing_extensions import TypedDict


class Parsed(TypedDict):
    name: str
    source_code: str
    hidden: bool


class ParsedParameter(Parsed):
    default_value: str
    type: str
    description: str


class ParsedReturn(TypedDict):
    type: str
    description: str


class ParsedFunction(Parsed):
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


class ParsedDocstring(TypedDict):
    description: str
    note: str
    examples: List[str]
    raises: List[str]
    returns: ParsedReturn
    parameters: List[ParsedParameter]
    attributes: List[ParsedParameter]


class ParsedVariable(Parsed):
    type: str
    description: str
    value: str


class ParsedClass(Parsed):
    functions: List[ParsedFunction]
    variables: List[ParsedVariable]
    description: str


class ParsedModule(Parsed):
    classes: List[ParsedClass]
    functions: List[ParsedFunction]
    variables: List[ParsedVariable]
