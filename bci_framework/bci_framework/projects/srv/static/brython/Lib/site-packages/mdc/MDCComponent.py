"""
Brython MDCComponent: MDCComponent
==================================


"""

from .core import MDCTemplate

########################################################################


class MDCComponent(MDCTemplate):
    """"""
    NAME = 'base', 'MDCComponent'

    # ----------------------------------------------------------------------
    def __new__(self, html_, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        return context['html_']

