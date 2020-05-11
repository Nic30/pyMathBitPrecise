import unittest
from pyMathBitPrecise.bit_utils import toggle_bit, align, iter_bits, mask_bytes,\
    reverse_bits


class BitUtilsTC(unittest.TestCase):

    def test_toogle_bit(self):
        self.assertEqual(toggle_bit(0b10, 1), 0b00)
        self.assertEqual(toggle_bit(0b10, 0), 0b11)

    def test_align(self):
        self.assertEqual(align(0xff, 4), 0xf0)
        self.assertEqual(align(0xff, 0), 0xff)

    def test_iter_bits(self):
        self.assertListEqual(list(iter_bits(0b1010, 4)), [0, 1, 0, 1])
        self.assertListEqual(list(iter_bits(0b0101, 4)), [1, 0, 1, 0])

    def test_mask_bytes(self):
        self.assertEqual(mask_bytes(0x010203, 0b101, 3), 0x010003)
        self.assertEqual(mask_bytes(0x010203, 0b010, 3), 0x000200)

    def test_reverse_bits(self):
        self.assertEqual(reverse_bits(0b011, 3), 0b110)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(BitUtilsTC(''))
    suite.addTest(unittest.makeSuite(BitUtilsTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
