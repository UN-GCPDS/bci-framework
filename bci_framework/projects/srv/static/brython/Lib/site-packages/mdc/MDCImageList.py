"""
Brython MDCComponent: MDCImageList
==================================


"""


from .core import MDCTemplate
#from .MDCButton import MDCButton,  MDCIconToggle


########################################################################
class __listItem__(MDCTemplate):
    """"""

    MDC_optionals = {

        'columns': 'width: calc(100% / {columns} - 2*{margin}px);',
        'margin': 'margin: {margin}px;',
        'margin_bottom': 'margin-bottom: {margin_bottom};',
        'label': '<div class="mdc-image-list__supporting"><span class="mdc-image-list__label">{label}</span></div>',


    }

    # ----------------------------------------------------------------------

    def __new__(self, columns, margin, masonry, src, label='', **kwargs):
        """"""
        if masonry:
            margin_bottom = margin
            columns = False
            margin = False

        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""

        if context['masonry']:
            code = """

              <li class="mdc-image-list__item image_container" style='{margin_bottom}'>
                <img class="mdc-image-list__image" src="{src}">
                {label}
              </li>

            """
        else:
            code = """

              <li class="mdc-image-list__item" style='{columns} {margin}'>
                <div class="mdc-image-list__image-aspect-container image_container" style="padding-bottom: 66.66667%;">
                  <img class="mdc-image-list__image" src="{src}" style="width: unset !important;">
                </div>
                {label}
              </li>

            """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------

    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'image_container':
            return self.element.select('.image_container')[0]

        elif name is 'label':
            return self.element.select('.mdc-image-list__supporting')[0]

        elif name is 'image':
            return self.element.select('.mdc-image-list__image')[0]

        # elif name is 'action_icons':
            # return self.element.select('.mdc-card__action-icons')[0]


########################################################################
class MDCImageList(MDCTemplate):
    """"""

    #NAME = 'LinearProgress'

    MDC_optionals = {

        # '_16_9': 'mdc-card__media--16-9',
        # 'square': 'mdc-card__media--square',
        'masonry': 'mdc-image-list--masonry masonry-image-list',
        'text_protection': 'mdc-image-list--with-text-protection',

        'masonry_column': 'column-count: {masonry_column};',
        'masonry_margin': 'column-gap: {masonry_margin};',


    }

    # ----------------------------------------------------------------------

    def __new__(self, columns=5, margin='2px', masonry=False, text_protection=False, **kwargs):
        """"""

        self.columns = columns
        self.margin = margin
        self.masonry = masonry

        if masonry:
            masonry_column = columns
            masonry_margin = margin
        else:
            masonry_column = False
            masonry_margin = False

        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""

        code = """
        <ul class="mdc-image-list {masonry} {text_protection}" style="{masonry_column} {masonry_margin}">
        </ul>
        """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------

    @classmethod
    def __getitem__(self, name):
        """"""
        # if name is 'actions':
            # return self.element.select('.mdc-card__actions')[0]

        # elif name is 'action_buttons':
            # return self.element.select('.mdc-card__action-buttons')[0]

        # elif name is 'action_icons':
            # return self.element.select('.mdc-card__action-icons')[0]

    # ----------------------------------------------------------------------
    @classmethod
    def add_item(cls, element, **kwargs):
        """"""
        item = __listItem__(cls.columns, cls.margin, cls.masonry, **kwargs)
        cls.element <= item
        return item
