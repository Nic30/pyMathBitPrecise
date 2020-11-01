import unittest
from pyMathBitPrecise.bit_utils import toggle_bit, align, iter_bits, mask_bytes,\
    reverse_bits, bit_list_to_int, int_list_to_int, extend_to_size,\
    bit_list_reversed_endianity, int_to_int_list,\
    bit_list_reversed_bits_in_bytes, apply_set_and_clear


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

    def test_bit_list_to_int(self):
        self.assertEqual(bit_list_to_int([0, 1]), 0b10)

    def test_int_list_to_int(self):
        self.assertEqual(int_list_to_int([0x1, 0x2, 0x3], 4), 0x321)

    def test_extend_to_size(self):
        self.assertListEqual(extend_to_size([], 2), [0, 0])
        self.assertListEqual(extend_to_size([1, ], 2), [1, 0])
        self.assertListEqual(extend_to_size([1, 2], 2), [1, 2])

    def test_bit_list_reversed_endianity(self):
        self.assertListEqual(bit_list_reversed_endianity(
            [1, 0, 1]), [1, 0, 1, 0, 0, 0, 0, 0])

    def test_bit_list_reversed_bits_in_bytes(self):
        bits = int_to_int_list(0x010203, 1, 3 * 8)
        rev_bits = bit_list_reversed_bits_in_bytes(bits)
        v = int_list_to_int(rev_bits, 1)
        self.assertEqual(v, 0x8040c0, "0x%x 0x%x" % (v, 0x8040c0))

    def test_apply_set_and_clear(self):
        self.assertEqual(apply_set_and_clear(0, 0b1010, 0), 0b1010)
        self.assertEqual(apply_set_and_clear(1, 0b1010, 0), 0b1011)
        self.assertEqual(apply_set_and_clear(1, 0b1010, 1), 0b1010)
        self.assertEqual(apply_set_and_clear(1, 0, 0b1010), 1)
        self.assertEqual(apply_set_and_clear(1, 0b1010, 0b1010), 0b1011)


if __name__ == '__main__':
    suite = unittest.TestSuite()
    # suite.addTest(BitUtilsTC(''))
    suite.addTest(unittest.makeSuite(BitUtilsTC))
    runner = unittest.TextTestRunner(verbosity=3)
    runner.run(suite)
