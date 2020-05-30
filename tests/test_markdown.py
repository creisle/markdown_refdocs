from markdown_refdocs.markdown import constant_to_markdown, function_to_markdown


class TestConstantToMarkdown:
    def test_no_source_code(self):
        md = constant_to_markdown({'name': 'SOME_CONSTANT', 'source_code': 'SOME_CONSTANT = "bob"'})
        assert (
            md
            == '''## SOME_CONSTANT

```python
SOME_CONSTANT = "bob"
```
'''
        )

    def test_has_source_code(self):
        md = constant_to_markdown({'name': 'SOME_CONSTANT', 'source_code': ''})
        assert (
            md
            == '''## SOME_CONSTANT
'''
        )


class TestFunctionToMarkdown:
    def test_has_docstring_no_params(self):
        md = function_to_markdown(
            {
                'name': 'some_func',
                'source_code': '',
                'source_definition': '',
                'description': 'some desc',
            }
        )
        assert (
            md
            == '''## some\\_func()

some desc
'''
        )
