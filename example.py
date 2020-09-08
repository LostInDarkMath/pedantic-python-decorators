from pedantic import pedantic_class

@pedantic_class
class MyClass:
    def __init__(self):
        print('test')

m = MyClass()