# Examples

## Function

Python input

```python
def parse_google_docstring(
    docstring: str, hide_undoc: bool = True, function_name=''
) -> ParsedDocstring:
    """
    parses a google-style docsting into a dictionary of the various sections
    """
    pass
```

Resulting markdown output (code block ticks escaped for display in this document)

```md
## parse\_google\_docstring()

parses a google-style docsting into a dictionary of the various sections

\`\`\`python
def parse_google_docstring(
    docstring: str, hide_undoc: bool = True, function_name=''
) -> ParsedDocstring:
\`\`\`

**Args**

- docstring (`str`)
- hide_undoc (`bool`)
- function_name

**Returns**

- [ParsedDocstring](../types/#class-parseddocstring)
```

## TypedDict Annotations

Python input

```python
class ParsedFunction(Parsed):
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
```

resulting markdown output

```md
## class ParsedFunction

**inherits** [Parsed](#parsed)

Result of the combination of parsing the source code and combining with the docstring of a function

**Attributes**

- parameters (List\[[ParsedParameter](#class-parsedparameter)\])
- returns ([ParsedReturn](#class-parsedreturn))
- note (`str`)
- raises (`List[str]`)
- examples (`List[str]`)
- description (`str`)
- is_static (`bool`)
- is_method (`bool`)
- is_class_method (`bool`)
- is_getter (`bool`)
```
