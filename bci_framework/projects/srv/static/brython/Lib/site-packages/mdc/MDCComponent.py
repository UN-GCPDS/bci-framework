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


#########################################################################
# class MDCLinearProgress(MDCTemplate):
    # """"""

    #NAME = 'LinearProgress'

    # CSS_classes = {

        # '_16_9': 'mdc-card__media--16-9',
        # 'square': 'mdc-card__media--square',
    # }

    # MDC_optionals = {

        # 'outlined': 'mdc-card--outlined',
        # 'full_bleed': 'mdc-card__actions--full-bleed',
        # 'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        # 'disabled': 'disabled',

    # }

    # ----------------------------------------------------------------------
    # def __new__(self, **kwargs):
        # """"""
        #self.element = self.render(locals(), kwargs)
        # return self.element

    # ----------------------------------------------------------------------
    # @classmethod
    # def __html__(cls, **context):
        # """"""

        # code = """

        # """

        # return cls.render_html(code, context)

    # ----------------------------------------------------------------------
    # @classmethod
    # def __getitem__(self, name):
        # """"""
        # if name is 'actions':
            # return self.element.select('.mdc-card__actions')[0]

        # elif name is 'action_buttons':
            # return self.element.select('.mdc-card__action-buttons')[0]

        # elif name is 'action_icons':
            # return self.element.select('.mdc-card__action-icons')[0]

    # ----------------------------------------------------------------------
    # @classmethod
    # def add_action_button(cls, mdc, *args, **kwargs):
        # """"""

    # ----------------------------------------------------------------------
    # @classmethod
    # def title(self, mdc, text):
        # """"""
        ##self['title'].text = text


