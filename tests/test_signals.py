import pytest
from easypy.signals import register_object, unregister_object, MissingIdentifier, PRIORITIES
from easypy.signals import on_test
from easypy.signals import on_test_identifier

on_test_identifier.identifier = 'obj'


def test_simple_signal_registration():

    @on_test.register
    def foo(a, b):
        a / b

    with pytest.raises(ZeroDivisionError):
        on_test(a=5, b=0, c='c')

    on_test.unregister(foo)
    on_test(a=5, b=0, c='c')


def test_simple_signal_object_registration():

    class Foo():
        def on_test(self, a, b):
            a / b
        __init__ = register_object

    f = Foo()

    with pytest.raises(ZeroDivisionError):
        on_test(a=5, b=0, c='c')

    unregister_object(f)


def test_simple_signal_object_identifier():

    on_test_identifier(obj='xxx')

    class Foo():
        def on_test_identifier(self, a):
            a / self.b
        __init__ = register_object

    f1 = Foo()
    f2 = Foo()

    f1.b = 1
    f2.b = 0

    with pytest.raises(MissingIdentifier):
        on_test_identifier(a=5, b=0, c='c')

    on_test_identifier(a=5, b=0, obj=f1)

    with pytest.raises(ZeroDivisionError):
        on_test_identifier(a=5, b=0, obj=f2)

    unregister_object(f1)
    unregister_object(f2)


def test_simple_signal_object_wo_identifier():

    class Foo():
        def on_test_identifier(self, obj):
            1 / 0
        __init__ = register_object

    f1 = Foo()

    with pytest.raises(ZeroDivisionError):
        on_test_identifier(a=5, b=0, obj='obj1')
        on_test_identifier(a=5, b=0, obj='obj2')

    unregister_object(f1)


def test_simple_signal_object_identifier_attribute():

    class Foo():
        def on_test_identifier(self):
            1 / 0
        __init__ = register_object

    f1 = Foo()
    f1.obj = 'obj1'

    on_test_identifier(obj='xxx')

    with pytest.raises(ZeroDivisionError):
        on_test_identifier(obj='obj1')

    unregister_object(f1)


def test_registration_context():

    def foo(a, b):
        a / b

    with on_test.registered(foo):
        with pytest.raises(ZeroDivisionError):
            on_test(a=5, b=0, c='c')

    on_test(a=5, b=0, c='c')


def test_priorities():

    l = []

    @on_test.register(priority=PRIORITIES.LAST)
    def last():
        l.append(3)

    @on_test.register(priority=PRIORITIES.FIRST)
    def first():
        l.append(1)

    @on_test.register()
    def mid():
        l.append(2)

    on_test()

    assert l == [1, 2, 3]


def test_async():
    from threading import get_ident

    main = get_ident()

    @on_test.register(async=True)
    def a1():
        assert get_ident() != main

    @on_test.register()
    def a2():
        assert get_ident() == main

    on_test()

    on_test.async = True

    @on_test.register()  # follows the current setting
    def a3():
        assert get_ident() != main

    on_test()

    on_test.async = False
