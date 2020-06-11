"""
Brython MDCComponent: MDCTopAppBar
==================================


"""


from .core import MDCTemplate
#from .MDCButton import MDCButton,  MDCIconToggle


# <a href="#" class="material-icons mdc-top-app-bar__action-item mdc-ripple-upgraded--unbounded mdc-ripple-upgraded" aria-label="Download" alt="Download" style="--mdc-ripple-fg-size:28.8px; --mdc-ripple-fg-scale:1.66667; --mdc-ripple-left:10px; --mdc-ripple-top:10px;">file_download</a>
# <a href="#" class="material-icons mdc-top-app-bar__action-item mdc-ripple-upgraded--unbounded mdc-ripple-upgraded" aria-label="Download" alt="Download" style="--mdc-ripple-fg-size:28.8px; --mdc-ripple-fg-scale:2.70424; --mdc-ripple-left:10px; --mdc-ripple-top:10px; --mdc-ripple-fg-translate-start:6.58438px, 9.6px; --mdc-ripple-fg-translate-end:9.6px, 9.6px;">file_download</a>


# <a href="#" class="material-icons mdc-top-app-bar__action-item mdc-ripple-upgraded--unbounded mdc-ripple-upgraded" aria-label="Download" alt="Download" style="--mdc-ripple-fg-size:28.8px; --mdc-ripple-fg-scale:1.66667; --mdc-ripple-left:10px; --mdc-ripple-top:10px;">file_download</a>
# <a href="#" class="material-icons mdc-top-app-bar__action-item mdc-ripple-upgraded--unbounded mdc-ripple-upgraded" aria-label="Download" alt="Download" style="--mdc-ripple-fg-size:28.8px; --mdc-ripple-fg-scale:1.66667; --mdc-ripple-left:10px; --mdc-ripple-top:10px;">file_download</a>


########################################################################
class __topAppBarItem__(MDCTemplate):
    """"""

    MDC_optionals = {

        'icon': '<a href="{href}" class="material-icons mdc-top-app-bar__action-item">{icon}</a>',
        'fa_icon': '<a href="{href}" class="material-icons mdc-top-app-bar__action-item"><i href="{href}" style="margin-left: 0px;" class="{fa_style} {fa_icon}"></i></a>',


    }

    # ----------------------------------------------------------------------
    def __new__(self, icon, href="#", **kwargs):
        """"""
        kwargs.update(self.format_icon(icon))
        del icon

        # if icon and icon.startswith('fa'):
            # fa_style = icon[:icon.find('-')]
            # fa_icon = 'fa' + icon[icon.find('-'):]
            # del icon

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


########################################################################
class MDCTopAppBar(MDCTemplate):
    """"""

    NAME = 'topAppBar', 'MDCTopAppBar'

    CSS_classes = {

        # '_16_9': 'mdc-card__media--16-9',
        # 'square': 'mdc-card__media--square',
    }

    MDC_optionals = {

        # 'outlined': 'mdc-card--outlined',
        # 'full_bleed': 'mdc-card__actions--full-bleed',
        # 'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        # 'disabled': 'disabled',

        'short': 'mdc-top-app-bar--short mdc-top-app-bar--short-has-action-item',
        'collapsed': 'mdc-top-app-bar--short-collapsed',
        'fixed': 'mdc-top-app-bar--fixed',
        'prominent': 'mdc-top-app-bar--prominent',
        'dense': 'mdc-top-app-bar--dense',

        # 'menu_icon': '<a href="#" class="material-icons mdc-top-app-bar__navigation-icon">{menu_icon}</a>',
        # 'menu_icon': '<a href="#" class="baseline-{menu_icon} mdc-top-app-bar__navigation-icon"></a>',

        # Icons
        'icon': '<a class="material-icons mdc-top-app-bar__navigation-icon">{icon}</a>',
        'fa_icon': '<a class="mdc-top-app-bar__navigation-icon {fa_style} {fa_icon}"></a>',

    }

    # ----------------------------------------------------------------------

    def __new__(self, title, icon='menu', items=[], short=False, collapsed=False, prominent=False, fixed=True, dense=False, theme='primary', **kwargs):
        """"""

        kwargs.update(self.format_icon(icon))
        del icon

        self.element = self.render(locals(), kwargs)
        self.element.autodrawer = True

        for item in items:
            self.add_item(item)

        # self.element.bind('MDCTopAppBar:nav', lambda ev:print('hdhd'))

        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""

        code = """

            <header class="mdc-top-app-bar app-bar mdc-theme--{theme}-bg mdc-theme--on-{theme} {short} {dense} {collapsed} {fixed} {prominent}" style='z-index: 1;'>
              <div class="mdc-top-app-bar__row">
                <section class="mdc-top-app-bar__section mdc-top-app-bar__section--align-start">
                  {icon}
                  {fa_icon}
                  <span class="mdc-top-app-bar__title">{title}</span>
                </section>
                <section class="mdc-top-app-bar__section mdc-top-app-bar__section--align-end" role="toolbar">
                </section>
              </div>
            </header>
        """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------

    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'actions':
            return self.element.select('.mdc-card__actions')[0]

        elif name is 'section_start':
            return self.element.select('.mdc-top-app-bar__section--align-start')[0]

        elif name is 'icons_parent':
            return self.element.select('.mdc-top-app-bar__section--align-end')[0]

        elif name is 'icon':
            return self.element.select('.mdc-top-app-bar__navigation-icon')[0]

        elif name is 'title':
            return self.element.select('.mdc-top-app-bar__title')[0]

    # ----------------------------------------------------------------------

    @classmethod
    def add_item(cls, element, *args, **kwargs):
        """"""

        item = __topAppBarItem__(*args, **kwargs)
        # print(cls['icons_parent'])
        cls['icons_parent'] <= item

        return item

    # ----------------------------------------------------------------------

    @classmethod
    def title(self, element, text):
        """"""
        self['title'].html = text

