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

        if not hasattr(self, '__orig_bases__'):
            raise AssertionError(
                f'{self.class_name} is not a generic class. To make it generic, declare it like: '
                f'class {self.class_name}(Generic[T], GenericMixin):...'
            )

        def collect(base, substitutions: dict[TypeVar, type]):
            """Recursively collect type var mappings from a generic base."""
            origin = get_origin(base) or base
            args = get_args(base)

            params = getattr(origin, '__parameters__', ())
            # copy substitutions so each recursion has its own view
            resolved = substitutions.copy()

            for param, arg in zip(params, args):
                if isinstance(arg, TypeVar):
                    arg = substitutions.get(arg, arg)
                mapping[param] = arg
                resolved[param] = arg

            # Recurse into base classes, applying current substitutions
            for super_base in getattr(origin, '__orig_bases__', []):
                super_origin = get_origin(super_base) or super_base
                super_args = get_args(super_base)

                if super_args:
                    # Substitute any TypeVars in the super_base's args using resolved
                    substituted_args = tuple(
                        resolved.get(a, a) if isinstance(a, TypeVar) else a
                        for a in super_args
                    )
                    # Build a new parametrized base so get_args() inside collect sees substituted_args
                    try:
                        substituted_base = super_origin[substituted_args]  # type: ignore[index]
                    except TypeError:
                        # Some origins won't accept subscription; fall back to passing the origin and trusting resolved
                        substituted_base = super_base
                    collect(base=substituted_base, substitutions=resolved)
                else:
                    collect(base=super_base, substitutions=resolved)

        # Start from __orig_class__ if present, else walk the declared MRO bases
        cls = getattr(self, '__orig_class__', None)
        if cls is not None:
            collect(base=cls, substitutions={})
        else:
            # Walk the full MRO to catch indirect generic ancestors
            for c in self.__class__.__mro__:
                for base in getattr(c, '__orig_bases__', []):
                    collect(base=base, substitutions=mapping)

        # Ensure no unresolved TypeVars remain
        all_params = set()
        for c in self.__class__.__mro__:
            all_params.update(getattr(c, '__parameters__', ()))

        unresolved = {p for p in all_params if p not in mapping or isinstance(mapping[p], TypeVar)}
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
