"""
Brython MDCComponent: MDCDialog
===============================


"""

from .core import MDCTemplate
from .MDCButton import MDCButton

########################################################################


class MDCDialog(MDCTemplate):
    """"""

    NAME = 'dialog', 'MDCDialog'

    CSS_classes = {

        # '_16_9': 'mdc-card__media--16-9',
        # 'square': 'mdc-card__media--square',
    }

    MDC_optionals = {

        'scrollable': 'mdc-dialog--scrollable',
        # 'full_bleed': 'mdc-card__actions--full-bleed',
        # 'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        # 'disabled': 'disabled',

    }

    # ----------------------------------------------------------------------
    def __new__(self, title='', content='', scrollable=False, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""
        cls.ID = cls.new_id()
        context['id'] = cls.ID

        code = """
        
        <div class="mdc-dialog"
             role="alertdialog"
             aria-modal="true"
             id="{id}"
             aria-labelledby="{id}-title"
             aria-describedby="{id}-content">
          <div class="mdc-dialog__container">
            <div class="mdc-dialog__surface">
              <h2 class="mdc-dialog__title" id="{id}-title">{title}</h2>
              <div class="mdc-dialog__content" id="{id}-content">
                {content}
              </div>
              <footer class="mdc-dialog__actions">
              </footer>
            </div>
          </div>
          <div class="mdc-dialog__scrim"></div>
        </div>        
        """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'actions':
            return self.element.select('.mdc-dialog__actions')[0]

        elif name is 'surface':
            return self.element.select('.mdc-dialog__surface')[0]

        elif name is 'content':
            return self.element.select('.mdc-dialog__content')[0]

        elif name is 'title':
            return self.element.select('.mdc-dialog__title')[0]

        # elif name is 'action_icons':
            # return self.element.select('.mdc-card__action-icons')[0]

    # ----------------------------------------------------------------------

    @classmethod
    def add_footer_button(cls, element, *args, **kwargs):
        """"""

        button = MDCButton(*args, **kwargs)
        button.class_name += ' mdc-dialog__button'

        if kwargs.get('action', False):
            button.attrs['data-mdc-dialog-action'] = kwargs['action']

        if kwargs.get('default', False):
            button.class_name += ' mdc-dialog__button--default'

        # if kwargs.get('cancel', False):
            # button.class_name += ' mdc-dialog__footer__button--cancel'
        # elif kwargs.get('accept', False):
            # button.class_name += ' mdc-dialog__footer__button--accept'

        # if kwargs.get('action', False):
            # button.class_name += ' mdc-dialog__action'

        if kwargs.get('theme', False):
            button.mdc.theme(kwargs['theme'])

        cls['actions'] <= button
        return button

    # ----------------------------------------------------------------------
    # @classmethod
    # def show(cls, *args, **kwargs):
        # """"""
        # dialog = window.mdc.dialog.MDCDialog.new(document.querySelector('#{}'.format(cls.ID)))
        # dialog.show()

    # ----------------------------------------------------------------------
    # @classmethod
    # def close(cls, *args, **kwargs):
        # """"""
        # dialog = window.mdc.dialog.MDCDialog.new(document.querySelector('#{}'.format(cls.ID)))
        # dialog.close()

    # ----------------------------------------------------------------------
    # @classmethod
    # def open(cls, *args, **kwargs):
        # """"""
        # dialog = window.mdc.dialog.MDCDialog.new(document.querySelector('#{}'.format(cls.ID)))
        # return dialog.open
