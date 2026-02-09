from typing import Generic, TypeVar, Any, List, Optional, Union

import pytest

from pedantic.constants import TYPE_VAR_METHOD_NAME, TYPE_VAR_SELF
from pedantic.decorators.class_decorators import pedantic_class
from pedantic.exceptions import PedanticTypeVarMismatchException

T = TypeVar('T')


def test_pedantic_generic_class():
    @pedantic_class
    class LoggedVar(Generic[T]):
        def __init__(self, value: T, name: str, logger: Any) -> None:
            self.name = name
            self.logger = logger
            self.value = value

        def set(self, new: T) -> None:
            self.log(message='Set ' + repr(self.value))
            self.value = new

        def get(self) -> T:
            self.log(message='Get ' + repr(self.value))
            return self.value

        def log(self, message: str) -> None:
            self.logger = self.name + message

    o = LoggedVar[int](value=42, name='hi', logger='test')
    o.set(new=57)
    assert isinstance(o.get(), int)

    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        o.set(new=3.14)


def test_stack():
    @pedantic_class
    class Stack(Generic[T]):
        def __init__(self) -> None:
            self.items: List[T] = []

        def push(self, item: T) -> None:
            self.items.append(item)

        def pop(self) -> T:
            return self.items.pop()

        def empty(self) -> bool:
            return not self.items

        def top(self) -> Optional[T]:
            if len(self.items) > 0:
                return self.items[len(self.items) - 1]
            else:
                return None

    my_stack = Stack[str]()
    get_type_vars = getattr(my_stack, TYPE_VAR_METHOD_NAME)
    assert get_type_vars() == {T: str, TYPE_VAR_SELF: Stack}
    with pytest.raises(expected_exception=IndexError):
        my_stack.pop()
    assert my_stack.top() is None
    assert my_stack.top() is None
    assert T in get_type_vars()
    my_stack.push(item='hi')
    assert T in get_type_vars()
    my_stack.push(item='world')
    assert T in get_type_vars()
    assert my_stack.pop() == 'world'
    assert my_stack.pop() ==  'hi'
    assert my_stack.top() is None

    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        my_stack.push(item=42)

    my_other_stack = Stack[int]()
    get_type_vars = getattr(my_other_stack, TYPE_VAR_METHOD_NAME)
    assert get_type_vars() == {T: int, TYPE_VAR_SELF: Stack}

    with pytest.raises(expected_exception=IndexError):
        my_other_stack.pop()

    assert my_other_stack.top() is None
    assert my_other_stack.top() is None
    my_other_stack.push(item=100)
    assert get_type_vars() == {T: int, TYPE_VAR_SELF: Stack}
    my_other_stack.push(item=142)
    assert get_type_vars() == {T: int, TYPE_VAR_SELF: Stack}
    assert my_other_stack.pop() == 142
    assert my_other_stack.pop() == 100
    assert my_other_stack.top() is None

    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        my_other_stack.push(item='42')


def test_generic_class_initialised_without_generics():
    @pedantic_class
    class MyClass(Generic[T]):
        def __init__(self, a: T) -> None:
            self.a = a

        def get_a(self) -> T:
            return self.a

        def set_a(self, val: T) -> None:
            self.a = val

    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        _ = MyClass(a=42)  # for some reason the exception is only raised when I assign it to a variable


def test_generic_class_initialised_without_generics_2():
    @pedantic_class
    class MyClass(Generic[T]):
        def __init__(self, a: T) -> None:
            self.a = a

        def get_a(self) -> T:
            return self.a

        def set_a(self, val: T) -> None:
            self.a = val

    MyClass(a=42)  # it is not recognized if it isn't assigned


def test_generic_class_inheritance():
    class Parent:
        pass

    class Child1(Parent):
        pass

    class Child2(Parent):
        pass

    @pedantic_class
    class MyClass(Generic[T]):
        def __init__(self, a: T) -> None:
            self.a = a

        def get_a(self) -> T:
            return self.a

        def set_a(self, val: T) -> None:
            self.a = val

    m = MyClass[Parent](a=Child1())
    assert isinstance(m.get_a(), Child1)
    assert not isinstance(m.get_a(), Child2)
    m.set_a(val=Child2())
    assert isinstance(m.get_a(), Child2)
    assert not isinstance(m.get_a(), Child1)


def test_merge_dicts():
    def create():
        @pedantic_class
        class MyClass(Generic[T]):
            def __init__(self, a: T) -> None:
                self.a = a

            def get_a(self) -> T:
                return self.a

            def set_a(self, val: T) -> None:
                self.a = val
        return MyClass(a=42)
    a = create()
    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        a.set_a(val='hi')


def test_recursion_depth_exceeded():
    @pedantic_class
    class Stack(Generic[T]):
        def __init__(self) -> None:
            self.items: List[T] = []

        def len(self) -> int:
            return len(self.items)

        def push(self, item: T) -> None:
            self.items.append(item)

        def pop(self) -> T:
            if len(self.items) > 0:
                return self.items.pop()
            else:
                raise ValueError()

        def empty(self) -> bool:
            return not self.items

        def top(self) -> Optional[T]:
            if len(self.items) > 0:
                return self.items[len(self.items) - 1]
            else:
                return None

        def __len__(self) -> int:
            return len(self.items)

    def create_stack():
        stack = Stack[int]()
        return stack

    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        stack: Stack[int] = Stack()
        stack.empty()

    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        stack = Stack()
        stack.empty()

    stack = create_stack()
    assert stack.empty()


def test_generic_union():
    @pedantic_class
    class Stack(Generic[T]):
        def __init__(self) -> None:
            self.items: List[T] = []

        def len(self) -> int:
            return len(self.items)

        def push(self, item: T) -> None:
            self.items.append(item)

        def pop(self) -> T:
            if len(self.items) > 0:
                return self.items.pop()
            else:
                raise ValueError()

        def empty(self) -> bool:
            return not self.items

        def top(self) -> Optional[T]:
            if len(self.items) > 0:
                return self.items[len(self.items) - 1]
            else:
                return None

        def __len__(self) -> int:
            return len(self.items)

    s = Stack[Union[int, float, str]]()
    s.push(item=42)
    s.push(item='hello')
    s.push(item=3.1415)

    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        s.push(item=[1, 2])


def test_inheritance():
    @pedantic_class
    class Stack(Generic[T]):
        def __init__(self) -> None:
            self.items: List[T] = []

        def len(self) -> int:
            return len(self.items)

        def push(self, item: T) -> None:
            self.items.append(item)

        def pop(self) -> T:
            if len(self.items) > 0:
                return self.items.pop()
            else:
                raise ValueError()

        def empty(self) -> bool:
            return not self.items

        def top(self) -> Optional[T]:
            if len(self.items) > 0:
                return self.items[len(self.items) - 1]
            else:
                return None

        def __len__(self) -> int:
            return len(self.items)

    @pedantic_class
    class Parent:
        pass

    @pedantic_class
    class Child1(Parent):
        pass

    @pedantic_class
    class Child2(Parent):
        pass

    parent_stack = Stack[Parent]()
    parent_stack.push(item=Child1())
    parent_stack.push(item=Child2())
    parent_stack.push(item=Parent())

    child_1_stack = Stack[Child1]()
    child_1_stack.push(item=Child1())
    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        child_1_stack.push(item=Child2())
    with pytest.raises(expected_exception=PedanticTypeVarMismatchException):
        child_1_stack.push(item=Parent())
