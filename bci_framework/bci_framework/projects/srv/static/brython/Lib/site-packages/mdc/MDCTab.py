"""
Brython MDCComponent: MDCTab
============================


"""


from .core import MDCTemplate

from browser import html, window
# from .MDCButton import MDCButton,  MDCIconToggle


########################################################################
class __tabItem__(MDCTemplate):
    """"""

    NAME = 'tab', 'MDCTab'

    MDC_optionals = {

        # 'outlined': 'mdc-card--outlined',
        # 'full_bleed': 'mdc-card__actions--full-bleed',
        'icon': '<span class="mdc-tab__icon material-icons" aria-hidden="true">{icon}</span>',

        # 'fa_icon': '<i class="mdc-button__icon {fa_style} {fa_icon}"></i>',
        'fa_icon': '<span class="mdc-tab__icon {fa_style} {fa_icon}"></span>',


        'active': 'mdc-tab--active',
        'indicator_active': 'mdc-tab-indicator--active',
        'stacked': 'mdc-tab--stacked',

    }

    # ----------------------------------------------------------------------

    def __new__(self, text=None, icon=None, id='#', stacked=False, active=False, **kwargs):
        """"""

        indicator_active = active

        if icon and icon.startswith('fa'):
            fa_style = icon[:icon.find('-')]
            fa_icon = 'fa' + icon[icon.find('-'):]
            del icon

        self.element = self.render(locals(), kwargs)
        self.element.bind('click', self.bind_click(self.element))

        self.element.indicator = window.mdc.tabIndicator.MDCTabIndicator.attachTo(self.element.select(".mdc-tab-indicator")[0])

        # self.element.bind('click', lambda ev: [button.deactivate() for button in self.element.parent.children])
        # self.element.bind('click', lambda ev: self.element.indicator.activate())

        # self.element.deactivate = self.element.indicator.deactivate

        return self.element

    # ----------------------------------------------------------------------
    @classmethod
    def bind_click(self, element):
        """"""
        def inset(event):
            [button.indicator.deactivate() for button in element.parent.children]
            element.indicator.activate()
            element.clicked()

        return inset

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""
        if context['text'] and not (context.get('icon', False) or context.get('fa_icon', False)):
            code = """
            <button class="mdc-tab {active}" role="tab" aria-selected="true">
              <span class="mdc-tab__content">
                <span class="mdc-tab__text-label">{text}</span>
              </span>

              <span class="mdc-tab-indicator {indicator_active}">
                <span class="mdc-tab-indicator__content mdc-tab-indicator__content--underline"></span>
              </span>

              <span class="mdc-tab__ripple"></span>
            </button>
            """

        elif not context['text'] and (context.get('icon', False) or context.get('fa_icon', False)):
            code = """
            <button class="mdc-tab {active}" role="tab" aria-selected="true">
              <span class="mdc-tab__content">
                {icon}
                {fa_icon}
              </span>
              <span class="mdc-tab-indicator {indicator_active}">
                <span class="mdc-tab-indicator__content mdc-tab-indicator__content--underline"></span>
              </span>
              <span class="mdc-tab__ripple"></span>
            </button>
            """

        elif context['text'] and (context.get('icon', False) or context.get('fa_icon', False)):
            code = """
            <button class="mdc-tab {active} {stacked}" role="tab" aria-selected="true">
              <span class="mdc-tab__content">
                {icon}
                {fa_icon}
                <span class="mdc-tab__text-label">{text}</span>
              </span>
              <span class="mdc-tab-indicator {indicator_active}">
                <span class="mdc-tab-indicator__content mdc-tab-indicator__content--underline"></span>
              </span>
              <span class="mdc-tab__ripple"></span>
            </button>
            """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------

    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'label':
            return self.element.select('.mdc-tab__text-label')[0]

        # elif name is 'items_location':
            # try:
                # return self.element.select('.mdc-tab-scroller__scroll-content')[0]
            # except:
                # return self.element


########################################################################
class MDCTabBar(MDCTemplate):
    """"""

    NAME = 'tabBar', 'MDCTabBar'

    CSS_classes = {

        # '_16_9': 'mdc-card__media--16-9',
        # 'square': 'mdc-card__media--square',
    }

    MDC_optionals = {

        # 'outlined': 'mdc-card--outlined',
        # 'full_bleed': 'mdc-card__actions--full-bleed',
        # 'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        # 'disabled': 'disabled',

    }

    # ----------------------------------------------------------------------

    def __new__(self, *items, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        self.element.panels = html.DIV(Class='panels')
        # self.element.mdc.bind('MDCTabBar:activated', self.__tabchanged__(self.element))

        self.element.stacked = kwargs.get('stacked', False)

        self.element.panel = {}

        for item in items:
            _, panel = self.add_item(self.element, **item)
            self.element.panel[item['id']] = panel

        return self.element

    # ----------------------------------------------------------------------
    @classmethod
    def __tabchanged__(cls, element, id, item):
        """"""
        # print('HHH', element.mdc, id)

        for e in element.select(".mdc-tab--active"):
            e.class_name = e.class_name.replace('mdc-tab--active', '')

        item.class_name += ' mdc-tab--active'

        try:

            for panel in element.panels.select('.panel'):
                panel.style = {'display': None, }

            # index = element.mdc.getFocusedTabIndex()
            element.panel[id].style = {'display': 'block', }

        except:
            pass
        # return inset

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
    <div class="mdc-tab-bar" role="tablist">
    <div class="mdc-tab-scroller">
    <div class="mdc-tab-scroller__scroll-area">
      <div class="mdc-tab-scroller__scroll-content">

      </div>
      </div>
      </div>
      </div>
        """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------

    @classmethod
    def __getitem__(self, name):
        """"""
        if name is 'items':
            return self.element.select('.mdc-tab')

        elif name is 'items_location':
            try:
                return self.element.select('.mdc-tab-scroller__scroll-content')[0]
            except:
                return self.element

        # elif name is 'action_icons':
            # return self.element.select('.mdc-card__action-icons')[0]

    # ----------------------------------------------------------------------

    @classmethod
    def add_item(cls, element, text=None, icon=None, id='#', active=False):
        """"""
        item = __tabItem__(text=text, icon=icon, id=id, active=active, stacked=element.stacked)
        item.clicked = lambda: cls.__tabchanged__(element, id, item)
        # item.bind('click', lambda event: cls.__tabchanged__(element, id, item))
        cls['items_location'] <= item

        if active:
            active = 'active'
            display = 'block'
        else:
            active = ''
            display = None

        panel = html.DIV(Class='panel {}'.format(active), id=id, role='tabpanel', aria_hidden=True)
        panel.style = {'display': display, }

        cls.element.panel[id] = panel
        cls.element.panels <= panel

        return item, panel

    # ----------------------------------------------------------------------
    # @classmethod
    # def title(self, mdc, text):
        # """"""
        # self['title'].text = text


########################################################################
class MDCTabScroller(MDCTabBar):
    """"""

    NAME = 'tabScroller', 'MDCTabScroller'

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""
        code = """
            <div class="mdc-tab-scroller">
              <div class="mdc-tab-scroller__scroll-area">
                <div class="mdc-tab-scroller__scroll-content"></div>
              </div>
            </div>
        """

        return cls.render_html(code, context)


