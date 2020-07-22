from typing import Optional, Union, Dict, List

from pyMathBitPrecise.bit_utils import ValidityError
from copy import copy


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

    def __getitem__(self, i):
        return Array3t(self, i)

    def bit_length(self) -> int:
        return self.size * self.element_t.bit_length()
    
    def _from_py(self, val, vld_mask):
        """
        from_py without normalization
        """
        return Array3val(self, val, vld_mask)

    def from_py(self, val: Union[List["value"], Dict[int, "value"], None],
                vld_mask: Optional[int]=None) -> "Array3val":
        """
        Construct value from pythonic value
        :note: str value has to start with base specifier (0b, 0h)
            and is much slower than the value specified
            by 'val' and 'vld_mask'. Does support x.
        """
        if val is None:
            val = {}
            vld_mask = 0
        elif isinstance(val, dict):
            _val = {}
            for k, v in val.items():
                k = int(k)
                if k < 0:
                    raise ValueError("item index < 0", k)

                if k >= self.size:
                    raise ValueError("item index >= array size", k)
                _val[k] = self.element_t.from_py(v)
            val = _val
        else:
            _val = {}
            for k, v in enumerate(val):
                if k >= self.size:
                    raise ValueError("item index >= array size", k)
                _val[k] = self.element_t.from_py(v)
            val = _val
        return Array3val(self, val, int(bool(vld_mask)))


class Array3val():
    """
    Value of Array3t.

    :note: use Array3t.from_py if you want to check the the type of val
    :ivar vld_mask: if 0 the value is entirely invalid else some item may be valid
    """

    def __init__(self, t: Array3t, val: Dict[int, object], vld_mask: int):
        """
        :param t: type of this value
        :param val: dict with items of this array
        :param vld_mask: validity flag for this value
        """
        self._dtype = t
        self.val = val
        self.vld_mask = vld_mask

    def __copy__(self):
        return self.__class__(self._dtype, copy(self.val), self.vld_mask)

    def __len__(self):
        ":return: size of this array"
        return self._dtype.size

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
            if index > self._dtype.size:
                raise IndexError(index)
        v = self.val[index] = self._dtype.element_t.from_py(None)
        return v

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

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.val)
