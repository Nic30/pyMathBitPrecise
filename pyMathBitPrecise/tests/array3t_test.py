import unittest

from pyMathBitPrecise.bit_utils import ValidityError
from pyMathBitPrecise.tests.bits3tBaseTC import uint8_t


class Array3tTC(unittest.TestCase):

    def test_1d_from_dict(self):
        v = uint8_t[4].from_py({i: i + 1 for i in range(4)})

        self.assertEqual(len(v), 4)
        for i, _v in zip(range(4), v):
            self.assertEqual(int(_v), i + 1)

        v = uint8_t[4].from_py({0: 1,
                                2: 3})
        self.assertEqual(len(v), 4)
        for i, _v in zip(range(4), v):
            if i in (0, 2):
                self.assertEqual(int(_v), i + 1)
            else:
                with self.assertRaises(ValidityError):
                    int(_v)

        v = uint8_t[4].from_py({})
        self.assertEqual(len(v), 4)
        for i, _v in zip(range(4), v):
            with self.assertRaises(ValidityError):
                int(_v)

        v = uint8_t[4].from_py(None)
        self.assertEqual(len(v), 4)
        for i, _v in zip(range(4), v):
            with self.assertRaises(ValidityError):
                int(_v)

        with self.assertRaises(ValueError):
            uint8_t[4].from_py({4: 4})

        with self.assertRaises(ValueError):
            uint8_t[4].from_py({-1: 4})

        for i in range(4):
            v[i] = i + 1
        for i, _v in zip(range(4), v):
            self.assertEqual(int(_v), i + 1)

    def test_2d_from_list(self):
        t = uint8_t[4][3]
        v = t.from_py([list(range(i * 4, (i + 1) * 4))
                       for i in range(3)])
        self.assertEqual(len(v), 3)
        self.assertEqual(len(v[0]), 4)
        for i, _v in zip(range(3), v):
            for i2, item in zip(range(4), _v):
                self.assertEqual(int(item), i * 4 + i2)
        with self.assertRaises(IndexError):
            v[4]
        with self.assertRaises(IndexError):
            v[0][5]


if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(Array3tTC('test_1d_from_dict'))
    suite.addTest(unittest.makeSuite(Array3tTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
