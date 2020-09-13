"""
Brython MDCComponent: MDCDrawer
===============================


"""

from browser import html
from .core import MDCTemplate


########################################################################
class __drawerItem__(MDCTemplate):
    """"""
    # NAME = 'draweritem', 'Drawer Item'

    MDC_optionals = {

        'ignore_link': 'RDNT-ignore_link',
        'icon': '<i class="material-icons mdc-list-item__graphic" aria-hidden="true">{icon}</i>',
        'fa_icon': '<i class="mdc-list-item__graphic {fa_style} {fa_icon}"></i>',

    }

    # ----------------------------------------------------------------------

    def __new__(self, name, icon=None, link='#', ignore_link=False, item_theme='', **kwargs):
        """"""
        if icon and icon.startswith('fa'):
            fa_style = icon[:icon.find('-')]
            fa_icon = 'fa' + icon[icon.find('-'):]
            del icon

        self.element = self.render(locals(), kwargs)

        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
        <a class="mdc-list-item {ignore_link}" href="{link}">
            {icon}
            {fa_icon}
            <span class="mdc-list-item__text">{name}</span>
        </a>
        """
        return cls.render_html(code, context)


########################################################################
class MDCDrawer(MDCTemplate):
    """"""

    CSS_classes = {
        # 'permanent': 'mdc-drawer--permanent',
        # 'fixed':  'mdc-toolbar--fixed',
        # 'waterfall': 'mdc-toolbar--waterfall',
        # 'flexible': 'mdc-toolbar--flexible',
        # 'fixed_lastrow_only': 'mdc-toolbar--fixed-lastrow-only',
    }

    # ----------------------------------------------------------------------
    def __new__(self, header='', mode='modal', theme='primary', item_theme=None, title='', subtitle='', **kwargs):
        """"""

        self.theme = theme
        # self.item_theme = item_theme

        if mode == 'modal':
            self.element = self.render(locals(), kwargs, attach_now=False)
            self.element.style = {'min-height': '100%'}
            self.element.attach = self.attach
        else:
            self.element = self.render(locals(), kwargs)
            self.element.style = {'min-height': '100%'}
            # self.element.attach = self.attach

        self.element.mode = mode

        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""

        context['theme_'] = {'primary': 'secondary',
                             'secondary': 'primary', }[context['theme']]

        # context['item_theme_'] = {'primary': 'secondary',
                                  # 'secondary': 'primary', }[context['item_theme']]

        cls.NAME = 'drawer', 'MDCDrawer'

        if context.get('mode') == 'permanent':
            code = """
                <aside class="mdc-drawer mdc-drawer--permanent">
                
                  <div class="mdc-drawer__header">
                    <h3 class="mdc-drawer__title">{title}</h3>
                    <h6 class="mdc-drawer__subtitle">{subtitle}</h6>
                  </div>
                
                  <div class="mdc-drawer__content">
                    <nav class="mdc-list">
                
                    </nav>
                  </div>
                </aside>
            """
        elif context.get('mode') == 'dismissible':
            code = """
                <aside class="mdc-drawer mdc-drawer--dismissible">
                
                  <div class="mdc-drawer__header">
                    <h3 class="mdc-drawer__title">{title}</h3>
                    <h6 class="mdc-drawer__subtitle">{subtitle}</h6>
                  </div>
                
                  <div class="mdc-drawer__content">
                    <nav class="mdc-list">
                
                    </nav>
                  </div>
                </aside>
            """

        elif context.get('mode') == 'modal':
            code = """
                <aside class="mdc-drawer mdc-drawer--modal">
                
                  <div class="mdc-drawer__header">
                    <h3 class="mdc-drawer__title">{title}</h3>
                    <h6 class="mdc-drawer__subtitle">{subtitle}</h6>
                  </div>
                
                  <div class="mdc-drawer__content">
                    <nav class="mdc-list">
                
                    </nav>
                  </div>
                </aside>
                
 
            """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------

    @classmethod
    def __getitem__(self, name):
        """"""
        try:

            if name is 'content':
                return self.element.select('.mdc-list')[0]
            elif name is 'items':
                return self.element.select('.mdc-list .mdc-list-item')
            elif name is 'header':
                return self.element.select('.mdc-drawer__header')[0]
            elif name is 'drawer_drawer':
                return self.element.select('.mdc-drawer__drawer')[0]

            # elif name is 'title':
                # return self.element.select('.mdc-toolbar__title')[0]

        except IndexError:
            return None

    # ----------------------------------------------------------------------

    @classmethod
    def add_item(cls, element, name, icon=None, link='#', **kwargs):
        """"""
        kwargs['item_theme'] = 'mdc-theme--{}'.format(cls.theme)

        item = __drawerItem__(name, icon, link, **kwargs)
        # print("IMHERE78")
        #item.bind('click', cls.__activate__(item))
        #item.bind('click', item.mdc.activate)

        cls['content'] <= item
        return item

    # ----------------------------------------------------------------------
    @classmethod
    def add_divider(cls, element, **kwargs):
        """"""
        kwargs['Class'] = 'mdc-list-divider ' + kwargs.get('Class', '')
        divider = html.HR(**kwargs)
        cls['content'] <= divider
        return divider

    # ----------------------------------------------------------------------
    @classmethod
    def add_subheader(cls, element, label, **kwargs):
        """"""
        kwargs['Class'] = 'mdc-list-group__subheader ' + kwargs.get('Class', '')
        subheader = html.H6(label, **kwargs)
        cls['content'] <= subheader
        return subheader

    # ----------------------------------------------------------------------
    # @classmethod
    # def __activate__(self, item):
        # """"""
        #inset = lambda evt:item.mdc.activate()
        # return inset

    # ----------------------------------------------------------------------
    # @classmethod
    # def activate(cls, item, *args, **kwargs):
        # """"""
        # print('EWE')

        # for it in document.select('.mdc-drawer .mdc-list-item'):
            #it.class_name = it.class_name.replace('mdc-list-item--activated', '')

        # item.mdc.add_class(['mdc-list-item--activated'])

    # ----------------------------------------------------------------------

    @classmethod
    def open(cls, element):
        """"""
        cls.mdc.open = True

    # ----------------------------------------------------------------------

    @classmethod
    def close(cls, element):
        """"""
        cls.mdc.open = False

    # ----------------------------------------------------------------------
    @classmethod
    def toggle(cls, element):
        """"""
        # print(cls.mdc.open)
        cls.mdc.open = not cls.mdc.open

