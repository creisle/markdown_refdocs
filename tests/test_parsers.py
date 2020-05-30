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
