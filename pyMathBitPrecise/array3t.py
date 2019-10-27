from typing import Optional, Union, Dict, List

from pyMathBitPrecise.bit_utils import ValidityError


class Array3t():

    def __init__(self, element_t, size: int, name: Optional[str]=None):
        self.element_t = element_t
        self.size = int(size)
        self.name = name

    def __eq__(self, other):
        return isinstance(other, self.__class__)\
            and self.size == other.size\
            and self.name == other.name\
            and self.element_t == other.element_t

    def bit_length(self) -> int:
        return self.size * self.element_t.bit_length()

    def from_py(self, val: Union[List["value"], Dict[int, "value"], None],
                vld_mask: Optional[int]=None) -> "ArrayVal":
        """
        Construct value from pythonic value
        :note: str value has to start with base specifier (0b, 0h)
            and is much slower than the value specified
            by 'val' and 'vld_mask'. Does support x.
        """
        if val is None:
            val = {}
        elif isinstance(val, dict):
            _val = {}
            for k, v in val.items():
                k = int(k)
                _val[k] = self.element_t.from_py(v)
            val = _val
        else:
            _val = {}
            for k, v in enumerate(val):
                k = int(k)
                _val[k] = self.element_t.from_py(v)
            val = _val
        return Array3val(self, val, 1)


class Array3val():
    """
    Value of Array3t

    :note: use Array3t.from_py if you want to check the the type of val
    """

    def __init__(self, t: Array3t, val, vld_mask: int):
        self._dtype = t
        self.val = val
        self.vld_mask = vld_mask

    def __getitem__(self, index):
        try:
            index = int(index)
        except ValidityError:
            index = None

        if index is not None:
            try:
                return self.val[index]
            except KeyError:
                pass
        return self._dtype.element_t.from_py(None)

    def __setitem__(self, index, val):
        try:
            index = int(index)
        except ValidityError:
            self.val.clear()
            return

        try:
            t = val._dtype
        except AttributeError:
            t = None

        if t is not None:
            assert t == self._dtype.element_t, (t, self._dtype.element_t)
        else:
            val = self._dtype.element_t.from_py(val)

        self.val[index] = val
