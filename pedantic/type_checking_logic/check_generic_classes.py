import inspect
from typing import Any, Generic, Dict

from pedantic.exceptions import PedanticTypeVarMismatchException
from pedantic.type_checking_logic.check_types import _get_type_arguments
from pedantic.constants import TypeVar, ATTR_NAME_GENERIC_INSTANCE_ALREADY_CHECKED


def check_instance_of_generic_class_and_get_typ_vars(instance: Any) -> Dict[TypeVar, Any]:
    """
        >>> from typing import TypeVar, Generic, List
        >>> T = TypeVar('T')
        >>> class A(Generic[T]): pass
        >>> a = A() # would normally raise an error due to _assert_constructor_called_with_generics, but not in doctest
        >>> check_instance_of_generic_class_and_get_typ_vars(a)
        {}
        >>> b = A[int]()
        >>> check_instance_of_generic_class_and_get_typ_vars(b)
        {~T: <class 'int'>}
        >>> c = A[List[int]]()
        >>> check_instance_of_generic_class_and_get_typ_vars(c)
        {~T: typing.List[int]}
        >>> S = TypeVar('S')
        >>> class B(Generic[T, S]): pass
        >>> d = B()
        >>> check_instance_of_generic_class_and_get_typ_vars(d)
        {}
        >>> e = B[int]()
        Traceback (most recent call last):
        ...
        TypeError: Too few parameters for ...; actual 1, expected 2
        >>> f = B[int, float]()
        >>> check_instance_of_generic_class_and_get_typ_vars(f)
        {~T: <class 'int'>, ~S: <class 'float'>}
        >>> class C(B): pass
        >>> g = C()
        >>> check_instance_of_generic_class_and_get_typ_vars(g)
        {}
    """
    type_vars = dict()
    _assert_constructor_called_with_generics(instance=instance)

    # The information I need is set after the object construction in the __orig_class__ attribute.
    # This method is called before construction and therefore it returns if the value isn't set
    # https://stackoverflow.com/questions/60985221/how-can-i-access-t-from-a-generict-instance-early-in-its-lifecycle
    if not hasattr(instance, '__orig_class__'):
        return type_vars

    type_variables = _get_type_arguments(type(instance).__orig_bases__[0])
    actual_types = _get_type_arguments(instance.__orig_class__)

    for i, type_var in enumerate(type_variables):
        type_vars[type_var] = actual_types[i]
    return type_vars


def _assert_constructor_called_with_generics(instance: Any) -> None:
    """
        This is very hacky. Therefore, it is kind of non-aggressive and raises only an error it is sure.

        >>> from typing import TypeVar, Generic, List
        >>> T = TypeVar('T')
        >>> class A(Generic[T]): pass
        >>> a = A() # would normally raise an error due to _assert_constructor_called_with_generics, but not in doctest
        >>> _assert_constructor_called_with_generics(a)
        >>> b = A[int]()
        >>> _assert_constructor_called_with_generics(b)
        >>> c = A[List[int]]()
        >>> _assert_constructor_called_with_generics(c)
        >>> S = TypeVar('S')
        >>> class B(Generic[T, S]): pass
        >>> d = B()
        >>> _assert_constructor_called_with_generics(d)
        >>> f = B[int, float]()
        >>> _assert_constructor_called_with_generics(f)
        >>> class C(B): pass
        >>> g = C()
        >>> _assert_constructor_called_with_generics(g)
    """

    if hasattr(instance, ATTR_NAME_GENERIC_INSTANCE_ALREADY_CHECKED):
        return

    name = instance.__class__.__name__
    q_name = instance.__class__.__qualname__
    call_stack_frames = inspect.stack()
    frame_of_wrapper = list(filter(lambda f: f.function == 'wrapper', call_stack_frames))
    if not frame_of_wrapper:
        return

    frame = call_stack_frames[call_stack_frames.index(frame_of_wrapper[-1]) + 1]
    while frame.filename.endswith('typing.py'):
        frame = call_stack_frames[call_stack_frames.index(frame) + 1]

    src = [_remove_comments_and_spaces_from_src_line(line) for line in inspect.getsource(frame.frame).split('\n')]
    target = '=' + name
    filtered_src = list(filter(lambda line: target in line, src))
    if not filtered_src:
        return

    for match in filtered_src:
        constructor_call = match.split(target)[1]
        generics = constructor_call.split('(')[0]
        if '[' not in generics or ']' not in generics:
            raise PedanticTypeVarMismatchException(
                f'Use generics when you create an instance of the generic class "{q_name}". \n '
                f'Your call: {match} \n How it should be called: {name}[YourType]({constructor_call.split("(")[1]}')

    setattr(instance, ATTR_NAME_GENERIC_INSTANCE_ALREADY_CHECKED, True)


def _is_instance_of_generic_class(instance: Any) -> bool:
    """
        >>> class A: pass
        >>> a = A()
        >>> _is_instance_of_generic_class(a)
        False
        >>> from typing import TypeVar, Generic
        >>> T = TypeVar('T')
        >>> class B(Generic[T]): pass
        >>> b = B()
        >>> _is_instance_of_generic_class(b)
        True
        >>> b2 = B[int]()
        >>> _is_instance_of_generic_class(b2)
        True
    """
    return Generic in instance.__class__.__bases__


def _remove_comments_and_spaces_from_src_line(line: str) -> str:
    """
        >>> _remove_comments_and_spaces_from_src_line('a = 42  # this is a comment')
        'a=42'
        >>> _remove_comments_and_spaces_from_src_line('m = MyClass[Parent](a=Child1())')
        'm=MyClass[Parent](a=Child1())'
    """
    return line.split('#')[0].replace(' ', '')


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
