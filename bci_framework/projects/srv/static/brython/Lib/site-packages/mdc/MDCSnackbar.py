"""
Brython MDCComponent: MDCSnackbar
=================================


"""

from .core import MDCTemplate
#from .MDCButton import MDCButton,  MDCIconToggle


########################################################################
class MDCSnackbar(MDCTemplate):
    """"""

    NAME = 'snackbar', 'MDCSnackbar'

    CSS_classes = {

        #'_16_9': 'mdc-card__media--16-9',
        #'square': 'mdc-card__media--square',
    }

    MDC_optionals = {

        #'outlined': 'mdc-card--outlined',
        #'full_bleed': 'mdc-card__actions--full-bleed',
        #'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        #'disabled': 'disabled',

        'align_start': 'mdc-snackbar--align-start',

    }

    #----------------------------------------------------------------------
    def __new__(self, align_start=False, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element



    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <div class="mdc-snackbar {align_start}" style="z-index: 999999"
                 aria-live="assertive"
                 aria-atomic="true"
                 aria-hidden="true">
              <div class="mdc-snackbar__text"></div>
              <div class="mdc-snackbar__action-wrapper">
                <button type="button" class="mdc-snackbar__action-button"></button>
              </div>
            </div>
        """
        return cls.render_html(code, context)




    #----------------------------------------------------------------------
    @classmethod
    def show(cls, element, message, action_text=None, action_handler=None, timeout=2750, multiline=False, actiononbottom=False):
        """"""

        if action_text and not action_handler:
            action_handler = lambda :None

        obj = {
            'message': message,
            'timeout': timeout,
            'actionHandler': action_handler,
            'actionText': action_text,
            'multiline': multiline,
            'actionOnBottom': actiononbottom,
        }

        cls.mdc.show(obj)


    #----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'text':
            return self.element.select('.mdc-snackbar__text')[0]

        #elif name is 'action_buttons':
            #return self.element.select('.mdc-card__action-buttons')[0]

        #elif name is 'action_icons':
            #return self.element.select('.mdc-card__action-icons')[0]


    #----------------------------------------------------------------------
    @classmethod
    def add_action_button(cls, element, mdc, *args, **kwargs):
        """"""



    ##----------------------------------------------------------------------
    #@classmethod
    #def title(self, mdc, text):
        #""""""
        #self['title'].text = text


