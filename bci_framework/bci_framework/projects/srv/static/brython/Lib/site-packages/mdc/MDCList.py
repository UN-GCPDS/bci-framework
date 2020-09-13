"""
Brython MDCComponent: MDCList
=============================


"""

from browser import html
from .core import MDCTemplate


########################################################################
class __listItem__(MDCTemplate):
    """"""

    MDC_optionals = {

        'meta': '<span class="mdc-list-item__meta">{meta}</span>',


        'icon_meta': '<a href="#" class="mdc-list-item__meta material-icons" onclick="event.preventDefault();" style="text-decoration: none; color: {meta_color};">{icon_meta}</a>',
        # 'fa_icon_meta': '<a href="#" class="mdc-list-item__meta material-icons" onclick="event.preventDefault();" style="text-decoration: none; color: {meta_color};">{icon_meta}</a>',


        'fa_icon_meta': '<i class="mdc-list-item__meta {fa_style_meta} {fa_icon_meta}" onclick="event.preventDefault();" style="text-decoration: none; color: {meta_color};"></i>',



        'icon': '<i class="material-icons mdc-list-item__graphic" aria-hidden="true">{icon}</i>',
        'fa_icon': '<i class="mdc-list-item__graphic {fa_style} {fa_icon}"></i>',



        'avatar': '<span class="mdc-list-item__graphic" style="background-color: {avatar_background_color}; color: {avatar_color};" role="presentation"><i class="material-icons" aria-hidden="true">{avatar}</i></span>',
        'placeholder': '<span class="mdc-list-item__graphic" style="background-color: {placeholder_background_color};"></span>',

    }

    # ----------------------------------------------------------------------

    def __new__(self, text, secondary_text=None, icon=False, icon_meta=False, meta=False, avatar=False, placeholder_background_coloiconr='rgba(0,0,0,.38)', avatar_color='white', meta_color='rgba(0,0,0,.38)', avatar_background_color='rgba(0,0,0,.38)', **kwargs):
        """"""

        if icon and icon.startswith('fa'):
            fa_style = icon[:icon.find('-')]
            fa_icon = 'fa' + icon[icon.find('-'):]
            del icon

        if icon_meta and icon_meta.startswith('fa'):
            fa_style_meta = icon_meta[:icon_meta.find('-')]
            fa_icon_meta = 'fa' + icon_meta[icon_meta.find('-'):]
            del icon_meta

        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""
        if context['secondary_text']:
            code = """
                <li class="mdc-list-item">
                  {icon}
                  {fa_icon}
                  {avatar}
                  {placeholder}
                  <span class="mdc-list-item__text">
                    <span class="mdc-list-item__primary-text">{text}</span>
                    <span class="mdc-list-item__secondary-text">{secondary_text}</span>
                  </span>
                  {meta}
                  {icon_meta}
                  {fa_icon_meta}
                </li>
            """

        else:
            code = """
                <li class="mdc-list-item">
                  {icon}
                  {avatar}
                  {placeholder}
                  <span class="mdc-list-item__text">{text}</span>
                  {meta}
                  {icon_meta}
                </li>
            """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------

    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'icon':
            return self.element.select('.mdc-list-item__graphic')[0]

        elif name is 'icon_meta':
            return self.element.select('.mdc-list-item__meta')[0]

        elif name is 'primary_text':
            return self.element.select('.mdc-list-item__primary-text')[0]


########################################################################
class __listChekItem__(MDCTemplate):
    """"""

    MDC_optionals = {

        'checked': 'checked=true',

    }

    # ----------------------------------------------------------------------

    def __new__(self, text, checked=False, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <li class="mdc-list-item checkbox-list-ripple-surface mdc-ripple-upgraded" style="--mdc-ripple-fg-size:360px; --mdc-ripple-fg-scale:1.6997692716423716; --mdc-ripple-fg-translate-start:258px, -163.06666564941406px; --mdc-ripple-fg-translate-end:120px, -156px;">
              <label for="trailing-checkbox-blueberries">{text}</label>
              <span class="mdc-list-item__meta">
                <div class="mdc-checkbox mdc-checkbox--upgraded mdc-ripple-upgraded mdc-ripple-upgraded--unbounded" style="--mdc-ripple-fg-size:24px; --mdc-ripple-fg-scale:1.6666666666666667; --mdc-ripple-left:8px; --mdc-ripple-top:8px;">
                  <input class="mdc-checkbox__native-control" {checked} id="trailing-checkbox-blueberries" type="checkbox">
                  <div class="mdc-checkbox__background">
                    <svg class="mdc-checkbox__checkmark" viewBox="0 0 24 24">
                      <path class="mdc-checkbox__checkmark-path" fill="none" stroke="white" d="M1.73,12.91 8.1,19.28 22.79,4.59"></path>
                    </svg>
                    <div class="mdc-checkbox__mixedmark"></div>
                  </div>
                </div>
              </span>
            </li>
        """
        return cls.render_html(code, context)


########################################################################
class MDCListGroup(MDCTemplate):
    """"""

    # ----------------------------------------------------------------------
    # def __new__(self, **kwargs):
        # """"""
        #self.element = self.render(locals(), kwargs)
        # return self.element

    # ----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <div class="mdc-list-group">
            </div>
        """
        return cls.render_html(code, context)

    # ----------------------------------------------------------------------

    @classmethod
    def add_list(cls, element, label, list_):
        """"""
        cls.element <= html.H3(label, Class='mdc-list-group__subheader')
        cls.element <= list_


########################################################################
class MDCList(MDCTemplate):
    """"""

    NAME = 'list', 'MDCList'

    MDC_optionals = {

        'two_line': 'mdc-list--two-line',
        'dense': 'mdc-list--two-line mdc-list--dense',
        'avatar': 'mdc-list--avatar-list',
        'non_interactive': 'mdc-list--non-interactive',

    }

    # ----------------------------------------------------------------------
    def __new__(self, two_line=False, dense=False, avatar=False, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <ul class="mdc-list {two_line} {dense} {avatar} {non_interactive}">
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

    # #----------------------------------------------------------------------
    # @classmethod
    # def add_action_button(cls, element, element, mdc, *args, **kwargs):
        # """"""

    # ----------------------------------------------------------------------
    @classmethod
    def add_item(cls, element, *args, **kwargs):
        """"""
        item = __listItem__(*args, **kwargs)
        cls.element <= item
        return item

    # ----------------------------------------------------------------------

    @classmethod
    def add_check_item(cls, element, *args, **kwargs):
        """"""
        item = __listChekItem__(*args, **kwargs)
        cls.element <= item
        return item

    # ----------------------------------------------------------------------

    @classmethod
    def add_divider(cls, element, hr=False, inset=False):
        """"""
        if inset:
            inset = 'mdc-list-divider--inset'
        else:
            inset = ''

        if hr:
            code = '<hr class="mdc-list-divider {inset}">'.format(inset=inset)
        else:
            code = '<li role="separator" class="mdc-list-divider {inset}"></li>'.format(inset=inset)
        code = cls.render_str(code)
        cls.element <= code

