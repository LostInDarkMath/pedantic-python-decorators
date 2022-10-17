from typing import List, Optional, Union
from unittest import TestCase

from pedantic.type_checking_logic.resolve_forward_ref import resolve_forward_ref


class TestResolveForwardRef(TestCase):
    def test_resolve_forward_ref_primitive_types(self):
        assert resolve_forward_ref(type_='int') == int
        assert resolve_forward_ref(type_='float') == float
        assert resolve_forward_ref(type_='str') == str
        assert resolve_forward_ref(type_='bool') == bool

    def test_resolve_forward_ref_typing_types(self):
        assert resolve_forward_ref(type_='List[int]') == List[int]
        assert resolve_forward_ref(type_='Optional[List[Union[str, float]]]') == Optional[List[Union[str, float]]]

    def test_unresolvable_type(self):
        with self.assertRaises(NameError):
            resolve_forward_ref(type_='Invalid')

    def test_resolve_forward_ref_custom_class(self):
        class Foo:
            pass

        context = locals()
        assert resolve_forward_ref(type_='Foo', context=context) == Foo
        assert resolve_forward_ref(type_='Optional[Foo]', context=context) == Optional[Foo]
