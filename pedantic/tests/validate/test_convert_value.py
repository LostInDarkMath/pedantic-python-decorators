from unittest import TestCase

from pedantic.decorators.fn_deco_validate.exceptions import ConversionError
from pedantic.decorators.fn_deco_validate.convert_value import convert_value


class TestConvertValue(TestCase):
    def test_convert_to_bool(self):
        for value in [True, 1, '1', '  1 ', '  tRuE  ', 'TRUE']:
            self.assertTrue(convert_value(value=value, target_type=bool))

        for value in [False, 0, '0', '  0 ', '  fAlSe  ', 'FALSE']:
            self.assertFalse(convert_value(value=value, target_type=bool))

        for value in ['alse', 0.1, '0.2', '  0000 ', 'Talse', 'Frue', 42]:
            with self.assertRaises(expected_exception=ConversionError):
                self.assertFalse(convert_value(value=value, target_type=bool))

    def test_convert_to_int(self):
        for value in range(-4, 4):
            self.assertEqual(value, convert_value(value=value, target_type=int))

        self.assertEqual(42, convert_value(value='42', target_type=int))
        self.assertEqual(0, convert_value(value='  0000 ', target_type=int))

        for value in ['alse', 'Talse', 'Frue', 0.2, '0.2']:
            with self.assertRaises(expected_exception=ConversionError):
                self.assertFalse(convert_value(value=value, target_type=int))

    def test_convert_to_float(self):
        for value in range(-4, 4):
            self.assertEqual(value, convert_value(value=value, target_type=float))

        self.assertEqual(0.2, convert_value(value=0.2, target_type=float))
        self.assertEqual(0.2, convert_value(value='0.2', target_type=float))
        self.assertEqual(42, convert_value(value='42', target_type=float))
        self.assertEqual(0, convert_value(value='  0000 ', target_type=float))

        for value in ['alse', 'Talse', 'Frue']:
            with self.assertRaises(expected_exception=ConversionError):
                self.assertFalse(convert_value(value=value, target_type=float))

    def test_convert_to_list(self):
        for value in [[], [1], ['1', '  1 '], ['  tRuE  ', 'TRUE']]:
            self.assertEqual(value, convert_value(value=value, target_type=list))

        self.assertEqual(['1', '2', '3'], convert_value(value='1,2,3', target_type=list))

    def test_convert_to_dict(self):
        for value in [{}, {1: 2}, {'1': '  1 '}, {1: '  tRuE  ', 2: 'TRUE'}]:
            self.assertEqual(value, convert_value(value=value, target_type=dict))

        self.assertEqual({'1': '1', '2': '4', '3': '7'}, convert_value(value='1:1,2:4,3:7', target_type=dict))



