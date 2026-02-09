from pedantic.decorators.class_decorators import trace_class


def test_trace_class():
    @trace_class
    class MyClass:
        def __init__(self, s: str) -> None:
            self.s = s

        def double(self, b: int) -> str:
            return self.s + str(b)

        @staticmethod
        def generator() -> 'MyClass':
            return MyClass(s='generated')

    m = MyClass.generator()
    m.double(b=42)

