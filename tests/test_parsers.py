from markdown_refdocs.parsers import parse_google_docstring


class TestParseGoogleDocstring:
    def test_nested_types(self):
        result = parse_google_docstring(
            """
Args:
    arg2 (List[Dict]): list of records
"""
        )
        assert len(result['parameters']) == 1
        assert result['parameters'][0]['type'] == 'List[Dict]'

    def test_add_extra_returns_to_description(self):
        result = parse_google_docstring(
            """
Returns:
    response: the response
    data (list, dict or None): The ids and type of resource object(s) in this relationship.
    meta (dict): meta information about the response
        total (int): total records available in the relationship
        count (int): total records returned in the response
        limit (int): the page size
        offset (int): starting point of the page
    links (dict): paging links to prev and next page, plus link to current request
"""
        )
        assert (
            result['returns']['description']
            == 'the response data (list, dict or None): The ids and type of resource object(s) in this relationship. meta (dict): meta information about the response total (int): total records available in the relationship count (int): total records returned in the response limit (int): the page size offset (int): starting point of the page links (dict): paging links to prev and next page, plus link to current request'
        )

    def test_long_docstring_with_newlines(self):
        result = parse_google_docstring(
            """
    Split the input text into a prefix and suffix, according to the following patterns:

    If the input string is letters followed by numbers, return them separately in a tuple.
    If the input string is only letters, return a tuple of ({letters}, None).
    If the input string is only numbers, return a tuple of (None, {numbers}).
    Otherwise return a tuple of Nones.
    Args:
        text (str): the input to split.
    Returns:
        tuple: The result of splitting the input string.
    Examples:
        prefix_split('A12345') == ('A', '12345')
        prefix_split('HTMCP_1') == ('HTMCP_', '1')
        prefix_split('ABC') == ('ABC', None)
        prefix_split('12345') == (None, '12345')
        prefix_split('A123B') == (None, None)"""
        )
        expected = """Split the input text into a prefix and suffix, according to the following patterns:

If the input string is letters followed by numbers, return them separately in a tuple.
If the input string is only letters, return a tuple of ({letters}, None).
If the input string is only numbers, return a tuple of (None, {numbers}).
Otherwise return a tuple of Nones."""
        assert result['description'] == expected
