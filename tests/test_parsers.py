from markdown_refdocs.parsers import parse_google_docstring


class ParseGoogleDocstring:
    def test_nested_types(self):
        result = parse_google_docstring(
            """
Args:
    arg2 (List[Dict]): list of records
"""
        )
        assert len(result['args']) == 1
        assert result['args']['type'] == 'List[Dict]'
