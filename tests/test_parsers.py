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
            result['returns']
            == 'the response data (list, dict or None): The ids and type of resource object(s) in this relationship. meta (dict): meta information about the response total (int): total records available in the relationship count (int): total records returned in the response limit (int): the page size offset (int): starting point of the page links (dict): paging links to prev and next page, plus link to current request'
        )
