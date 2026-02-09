from typing import List, Optional, Union

import pytest

from pedantic.type_checking_logic.resolve_forward_ref import resolve_forward_ref


def test_resolve_forward_ref_primitive_types():
    assert resolve_forward_ref(type_='int') == int
    assert resolve_forward_ref(type_='float') == float
    assert resolve_forward_ref(type_='str') == str
    assert resolve_forward_ref(type_='bool') == bool

def test_resolve_forward_ref_typing_types():
    assert resolve_forward_ref(type_='List[int]') == List[int]
    assert resolve_forward_ref(type_='Optional[List[Union[str, float]]]') == Optional[List[Union[str, float]]]

def test_unresolvable_type():
    with pytest.raises(NameError):
        resolve_forward_ref(type_='Invalid')

def test_resolve_forward_ref_custom_class():
    class Foo:
        pass

    context = locals()
    assert resolve_forward_ref(type_='Foo', context=context) == Foo
    assert resolve_forward_ref(type_='Optional[Foo]', context=context) == Optional[Foo]
