from collections import OrderedDict
from typing import List, Optional

from pyMathBitPrecise.bits3t import Bits3val


class Enum3val():

    def __init__(self, t, val, vld_mask):
        self._dtype = t
        self.val = val
        self.vld_mask = vld_mask

    def __copy__(self):
        return self.__class__(self._dtype, self.val, self.vld_mask)

    def _eq(self, other):
        t = other._dtype
        if self._dtype is not t:
            raise TypeError(other)
        val = self.val == other.val
        vld_mask = self.vld_mask & other.vld_mask
        return Bits3val._BOOL._from_py(int(val), int(vld_mask))

    def __ne__(self, other):
        t = other._dtype
        if self._dtype is not t:
            raise TypeError()
        val = self.val != other.val
        vld_mask = self.vld_mask & other.vld_mask
        return Bits3val._BOOL._from_py(int(val), int(vld_mask))

    def _is(self, other):
        return isinstance(other, Enum3val)\
            and other._dtype is self._dtype\
            and self.val == other.val\
            and self.vld_mask == other.vld_mask

    def __hash__(self):
        return hash((self._dtype, self.val, self.vld_mask))

    def __repr__(self):
        cls_name = self._dtype.__class__.__name__
        if self.vld_mask:
            return "<%s.%s>" % (cls_name, self.val)
        else:
            return "<%s invalid>" % cls_name


class Enum3tMeta(type):

    @classmethod
    def __prepare__(metacls, cls, bases):
        return OrderedDict()

    def __new__(metacls, cls, bases, classdict):
        ignored_props = {"from_py"}
        all_values = []
        for k, v in classdict.items():
            if k.startswith("__") or k in ignored_props:
                continue
            new_v = Enum3val(None, k, 1)
            classdict[k] = new_v
            all_values.append(new_v)

        enum_class = super().__new__(metacls, cls, bases, classdict)
        enum_class._all_values = all_values
        t_inst = enum_class()
        for v in all_values:
            v._dtype = t_inst
        return enum_class


class Enum3t(metaclass=Enum3tMeta):
    """
    :note: use as Python enum.Enum,
        the value is always ignored and name is used as a value
    """
    def __new__(cls):
        obj = cls.__dict__.get("__instance__", None)
        if obj is not None:
            # only own property
            return obj
        obj = super().__new__(cls)
        cls.__instance__ = obj
        return obj

    def __eq__(self, other):
        return self.__class__ == other.__class__

    def _from_py(self, val, vld_mask):
        """
        from_py without normalization
        """
        return Enum3val(self, val, vld_mask)

    def from_py(self, val: None,
                vld_mask: Optional[int]=None) -> Enum3val:
        """
        :attention: Used only in initialization, use enum class properties
            if you want to get a value
        """
        if val is not None or vld_mask is not None:
            raise NotImplementedError()
        return Enum3val(self, None, 0)


def define_Enum3t(name: str, values: List[str]):
    """
    Define Enum3t subclass from enum names
    """
    cls_dict = OrderedDict()
    for v in values:
        cls_dict[v] = None
    return type(name, (Enum3t,), cls_dict)
