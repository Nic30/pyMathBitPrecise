import unittest

from pyMathBitPrecise.enum3t import Enum3t, define_Enum3t, Enum3val


class Enum3tTC(unittest.TestCase):

    def test_instantiation_and_eq_neq(self):
        class Enum0(Enum3t):
            (A, B, C) = range(3)
        Enum1 = define_Enum3t("Enum1", ["A", "B", "C"])
        self.assertIsInstance(Enum0.A, Enum3val)
        self.assertIsInstance(Enum1.A, Enum3val)
        self.assertEqual(Enum0.A, Enum0.A)
        self.assertTrue(Enum0.A._eq(Enum0.A))
        self.assertFalse(Enum0.A._eq(Enum0.B))
        with self.assertRaises(TypeError):
            Enum0.A._eq(Enum1.B)

        self.assertNotEqual(Enum0.A, Enum0.B)
        with self.assertRaises(TypeError):
            Enum0.A != Enum1.A
        r = Enum0.A != Enum3val(Enum0.C._dtype, None, 0)
        self.assertEqual(r.vld_mask, 0)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(Enum3tTC('test_instantiation_and_eq_neq'))
    suite.addTest(unittest.makeSuite(Enum3tTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
