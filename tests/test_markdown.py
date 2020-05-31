from markdown_refdocs.markdown import constant_to_markdown, create_type_link, function_to_markdown


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


class TestCreateTypeLink:
    def test_simple_link(self):
        link = './path/to/other/#class-someclass'
        types = {'type': link}
        md = create_type_link('type', types)
        assert md == f'[type]({link})'

    def test_link_inside_list(self):
        link = './path/to/other/#class-someclass'
        types = {'type': link}
        md = create_type_link('List[type]', types)
        assert md == f'List\\[[type]({link})\\]'
