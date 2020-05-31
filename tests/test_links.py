from markdown_refdocs.links import create_relative_types_mapping, create_types_mapping
from markdown_refdocs.types import ParsedClass, ParsedModule, ParsedVariable


class TestCreateTypesMapping:
    def test_class_same_file(self) -> None:
        inputs = {
            'path/mod1': ParsedModule(
                {
                    'name': 'mod1',
                    'classes': [ParsedClass({'name': 'SomeClass'})],
                    'variables': [ParsedVariable({'name': 'SOME_VARIABLE', 'type': 'SomeClass'})],
                }
            )
        }
        mapping = create_types_mapping(inputs)
        assert mapping == {
            'SomeClass': './path/mod1/#class-someclass',
            'mod1.SomeClass': './path/mod1/#class-someclass',
        }

    def test_drop_name_clashes(self) -> None:
        inputs = {
            'path/mod1': ParsedModule(
                {
                    'name': 'mod1',
                    'classes': [ParsedClass({'name': 'SomeClass'})],
                    'variables': [ParsedVariable({'name': 'SOME_VARIABLE', 'type': 'SomeClass'})],
                }
            ),
            'path/mod2': ParsedModule(
                {
                    'name': 'mod2',
                    'classes': [ParsedClass({'name': 'SomeClass'})],
                    'variables': [ParsedVariable({'name': 'SOME_VARIABLE', 'type': 'SomeClass'})],
                }
            ),
        }
        mapping = create_types_mapping(inputs)
        assert mapping == {
            'mod1.SomeClass': './path/mod1/#class-someclass',
            'mod2.SomeClass': './path/mod2/#class-someclass',
        }

    def test_class_other_file(self) -> None:
        inputs = {
            'path/mod1': ParsedModule(
                {'name': 'mod1', 'classes': [ParsedClass({'name': 'SomeClass'})]}
            ),
            'path/mod2': ParsedModule(
                {
                    'name': 'mod2',
                    'variables': [ParsedVariable({'name': 'SOME_VARIABLE', 'type': 'SomeClass'})],
                }
            ),
        }
        mapping = create_types_mapping(inputs)
        assert mapping == {
            'SomeClass': './path/mod1/#class-someclass',
            'mod1.SomeClass': './path/mod1/#class-someclass',
        }


class TestCreateRelativeTypesMapping:
    def test_self_links(self):
        initial = {
            'type1': 'things/thing1.md/#class-firstclass',
            'type2': 'things/thing2.md/#class-firstclass',
        }
        relative = {
            'type1': '#class-firstclass',
            'type2': '../thing2/#class-firstclass',
        }
        assert create_relative_types_mapping('things/thing1.md', initial) == relative
