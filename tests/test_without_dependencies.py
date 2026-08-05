"""Those tests should work even without optional dependencies."""

def test_import_stuff():
    from pedantic import Validator  # noqa: PLC0415
    assert Validator.__name__ == 'Validator'
