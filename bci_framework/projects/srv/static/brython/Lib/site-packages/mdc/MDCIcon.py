"""
Brython MDCComponent: MDCIcon
===============================
"""
from .core import MDCTemplate


########################################################################
class MDCIcon(MDCTemplate):
    """"""

    NAME = None, None

    MDC_optionals = {

        # Icons
        'icon': '<i class="material-icons mdc-button__icon" {reversed} aria-hidden="true">{icon}</i>',
        'fa_icon': '<i class="mdc-button__icon {fa_style} {fa_icon}"></i>',

    }

    # ----------------------------------------------------------------------
    def __new__(self, icon, size=None, **kwargs):
        """"""
        kwargs.update(self.format_icon(icon))
        del icon

        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            {icon}
            {fa_icon}
            """

        return cls.render_html(code, context)

