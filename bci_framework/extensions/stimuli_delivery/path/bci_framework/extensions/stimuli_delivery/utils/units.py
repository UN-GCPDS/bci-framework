from bci_framework.extensions import properties as prop
from typing import Union
from math import radians, tan
import logging


########################################################################
class Units:
    """"""
    d = 0.7112

    # ----------------------------------------------------------------------
    def __init__(self, dpi: Union[None, int, float] = None, d: Union[None, int, float] = None):
        """"""
        if dpi:
            setattr(Units, '_dpi', dpi)
        if d:
            setattr(Units, 'd', d)

    # ----------------------------------------------------------------------
    @classmethod
    def dpi(cls):
        """"""
        if dpi := getattr(cls, '_dpi', None):
            return dpi
        else:
            return prop.DPI

    # ----------------------------------------------------------------------
    def __call__(self, dpi: Union[None, int, float] = None, d: Union[None, int, float] = None):
        """"""
        if dpi:
            setattr(Units, '_dpi', dpi)
        if d:
            setattr(Units, 'd', d)

    # ----------------------------------------------------------------------
    @classmethod
    def scale(cls, value: Union[int, float], dpi: Union[None, int, float] = None) -> Union[int, float]:
        """"""
        if dpi is None:
            dpi = cls.dpi()
        return value * float(dpi) / 96

    # ----------------------------------------------------------------------
    @classmethod
    def dva(cls, value: Union[int, float], d: Union[None, int, float] = None, dpi: Union[None, int, float] = None, scale: Union[None, int, float] = 1) -> str:
        """"""
        assert not (
            d is None and cls.d is None), "Must define d, as 'distance from monitor'"
        if d is None:
            d = cls.d

        return f"{cls.scale(2*d*39.37*tan((radians(value)/2))*96*scale, dpi)}px"
