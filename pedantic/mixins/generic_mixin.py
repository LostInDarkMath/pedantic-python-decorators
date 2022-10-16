from typing import List, Type, TypeVar, Dict, Generic


class GenericMixin:
    """
        A mixin that provides easy access to given type variables.

        Example:
            >>> from typing import Generic, TypeVar
            >>> T = TypeVar('T')
            >>> U = TypeVar('U')
            >>> class Foo(Generic[T, U], GenericMixin):
            ...     values: List[T]
            ...     value: U
            >>> f = Foo[str, int]()
            >>> f.type_vars
            {~T: <class 'str'>, ~U: <class 'int'>}
    """

    @property
    def type_var(self) -> Type:
        """
            Get the type variable for this class.
            Use this for convenience if your class has only one type parameter.

            Example:
                >>> from typing import Generic, TypeVar
                >>> T = TypeVar('T')
                >>> class Foo(Generic[T], GenericMixin):
                ...     value: T
                >>> f = Foo[float]()
                >>> f.type_var
                <class 'float'>
        """

        types = self._get_types()
        assert len(types) == 1, f'You have multiple type parameters. Please use "type_vars" instead of "type_var".'
        return list(types.values())[0]  # type: ignore

    @property
    def type_vars(self) -> Dict[TypeVar, Type]:
        """
            Returns the mapping of type variables to types.

            Example:
                >>> from typing import Generic, TypeVar
                >>> T = TypeVar('T')
                >>> U = TypeVar('U')
                >>> class Foo(Generic[T, U], GenericMixin):
                ...     values: List[T]
                ...     value: U
                >>> f = Foo[str, int]()
                >>> f.type_vars
                {~T: <class 'str'>, ~U: <class 'int'>}
        """

        return self._get_types()

    def _get_types(self) -> Dict[TypeVar, Type]:
        """
            See https://stackoverflow.com/questions/57706180/generict-base-class-how-to-get-type-of-t-from-within-instance/60984681#60984681
        """

        non_generic_error = AssertionError(
            f'{self.class_name} is not a generic class. To make it generic, declare it like: '
            f'class {self.class_name}(Generic[T], GenericMixin):...')

        if not hasattr(self, '__orig_bases__'):
            raise non_generic_error

        generic_bases = [c for c in self.__orig_bases__ if hasattr(c, '__origin__') and c.__origin__ == Generic]

        if not generic_bases:
            raise non_generic_error

        generic_base = generic_bases[0]  # this is safe because a class can have at most one "Generic" superclass

        if not hasattr(self, '__orig_class__'):
            raise AssertionError(
                f'You need to instantiate this class with type parameters! Example: {self.class_name}[int]()')

        types = self.__orig_class__.__args__  # type: ignore
        type_vars = generic_base.__args__
        return {v: t for v, t in zip(type_vars, types)}

    @property
    def class_name(self) -> str:
        """ Get the name of the class of this instance. """

        return type(self).__name__


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
