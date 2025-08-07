from typing import Type, TypeVar, Dict, get_origin, get_args


class GenericMixin:
    """
        A mixin that provides easy access to given type variables.

        Example:
            >>> from typing import Generic, TypeVar
            >>> T = TypeVar('T')
            >>> U = TypeVar('U')
            >>> class Foo(Generic[T, U], GenericMixin):
            ...     values: list[T]
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

            DO NOT call this inside __init__()!

            Example:
                >>> from typing import Generic, TypeVar
                >>> T = TypeVar('T')
                >>> class Foo(Generic[T], GenericMixin):
                ...     value: T
                >>> f = Foo[float]()
                >>> f.type_var
                <class 'float'>
        """

        types = self._get_resolved_typevars()
        assert len(types) == 1, f'You have multiple type parameters. Please use "type_vars" instead of "type_var".'
        return list(types.values())[0]  # type: ignore

    @property
    def type_vars(self) -> Dict[TypeVar, Type]:
        """
            Returns the mapping of type variables to types.

            DO NOT call this inside __init__()!

            Example:
                >>> from typing import Generic, TypeVar
                >>> T = TypeVar('T')
                >>> U = TypeVar('U')
                >>> class Foo(Generic[T, U], GenericMixin):
                ...     values: list[T]
                ...     value: U
                >>> f = Foo[str, int]()
                >>> f.type_vars
                {~T: <class 'str'>, ~U: <class 'int'>}
        """

        return self._get_resolved_typevars()

    def _get_resolved_typevars(self) -> Dict[TypeVar, Type]:
        """
        Do not call this inside the __init__() method, because at that point the relevant information are not present.
        See also https://github.com/python/cpython/issues/90899'
        """

        mapping: dict[TypeVar, type] = {}

        non_generic_error = AssertionError(
            f'{self.class_name} is not a generic class. To make it generic, declare it like: '
            f'class {self.class_name}(Generic[T], GenericMixin):...')

        if not hasattr(self, '__orig_bases__'):
            raise non_generic_error

        def collect(base, substitutions: dict[TypeVar, type]) -> None:
            origin = get_origin(base)
            args = get_args(base)

            if origin is None:
                return

            params = getattr(origin, '__parameters__', ())
            resolved = {}
            for param, arg in zip(params, args):
                resolved_arg = substitutions.get(arg, arg) if isinstance(arg, TypeVar) else arg
                mapping[param] = resolved_arg
                resolved[param] = resolved_arg

            for super_base in getattr(origin, '__orig_bases__', []):
                collect(super_base, resolved)

        # Prefer __orig_class__ if available
        cls = getattr(self, '__orig_class__', None)
        if cls is not None:
            collect(base=cls, substitutions={})
        else:
            for base in getattr(self.__class__, '__orig_bases__', []):
                collect(base=base, substitutions={})

        # Extra safety: ensure all declared typevars are resolved
        all_params = set()
        for cls in self.__class__.__mro__:
            all_params.update(getattr(cls, '__parameters__', ()))

        unresolved = {param for param in all_params if param not in mapping or isinstance(mapping[param], TypeVar)}
        if unresolved:
            raise AssertionError(
                f'You need to instantiate this class with type parameters! Example: {self.class_name}[int]()\n'
                f'Also make sure that you do not call this in the __init__() method of your class!\n'
                f'Unresolved type variables: {unresolved}\n'
                f'See also https://github.com/python/cpython/issues/90899'
            )

        return mapping

    @property
    def class_name(self) -> str:
        """ Get the name of the class of this instance. """

        return type(self).__name__


if __name__ == '__main__':
    import doctest
    doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
