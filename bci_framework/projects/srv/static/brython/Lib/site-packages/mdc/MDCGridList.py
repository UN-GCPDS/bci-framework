"""
Brython MDCComponent: MDCGridList
=================================


"""


from .core import MDCTemplate
# from browser import html
#from .MDCButton import MDCButton,  MDCIconToggle


#########################################################################
# class __Tile__(MDCTemplate):

    # ----------------------------------------------------------------------
    # @classmethod
    # def __html__(cls, **context):
        # """"""

        # code = """
            # <li class="mdc-grid-tile">
            # </li>
        # """


########################################################################
class __gridTile__(MDCTemplate):

    NAME = 'gridtile', 'MDCGridTile'

    MDC_optionals = {

        # 'outlined': 'mdc-card--outlined',
        # 'full_bleed': 'mdc-card__actions--full-bleed',
        'icon': '<i class="mdc-grid-tile__icon material-icons">{icon}</i>',
        # 'disabled': 'disabled',
        'img': '<img class="mdc-grid-tile__primary-content" src="{img}"/>',
        'div': '<div class="mdc-grid-tile__primary-content" style="background-image: url({div});"></div>',
        'caption': '<span class="mdc-grid-tile__support-text">{caption}</span>',


    }

    # ----------------------------------------------------------------------
    def __new__(self, title, caption=None, img=None, div=None, theme='primary', **kwargs):
        """"""

        self.theme = theme

        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""

        context['theme_'] = {'primary': 'secondary',
                             'secondary': 'primary', }[context['theme']]

        code = """
            <li class="mdc-grid-tile">
              <div class="mdc-grid-tile__primary">
                {img}
                {div}
              </div>
              <span class="mdc-grid-tile__secondary mdc-theme--{theme_}-bg">
                {icon}
                <span class="mdc-grid-tile__title">{title}</span>
                {caption}
              </span>
            </li>
        """

        return cls.render_html(code, context)

    # ----------------------------------------------------------------------
    # @classmethod
    # def new_tile(cls, mdc, *args, **kwargs):
        # """"""
        #tile = __Tile__()
        #cls.element <= tile
        # return tile


########################################################################
class MDCGridList(MDCTemplate):
    """"""

    NAME = 'gridList', 'MDCGridList'

    CSS_classes = {

        # '_16_9': 'mdc-card__media--16-9',
        # 'square': 'mdc-card__media--square',
    }

    MDC_optionals = {

        # 'outlined': 'mdc-card--outlined',
        # 'full_bleed': 'mdc-card__actions--full-bleed',
        'icon_start': 'mdc-grid-list--with-icon-align-start',
        'icon_end': 'mdc-grid-list--with-icon-align-end',
        'aspect_ratio': 'mdc-grid-list--tile-aspect-{aspect_ratio}',
        'caption': 'mdc-grid-list--twoline-caption',
        # 'disabled': 'disabled',

    }

    # ----------------------------------------------------------------------
    def __new__(self, aspect_ratio='16x9', icon_start=False, icon_end=False, **kwargs):
        """"""
        self.element = self.render(locals(), kwargs)
        return self.element

    # ----------------------------------------------------------------------

    @classmethod
    def __html__(cls, **context):
        """"""

        code = """
            <div class="mdc-grid-list {icon_start} {icon_end} {aspect_ratio} {caption}">
              <ul class="mdc-grid-list__tiles">

              </ul>
            </div>
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
    def grid_tile(cls, element, *args, **kwargs):
        """"""
        grid_tile = __gridTile__(*args, **kwargs)
        cls.element <= grid_tile
        return grid_tile

    # ----------------------------------------------------------------------
    # @classmethod
    # def new_grid_tile(cls, mdc, *args, **kwargs):
        # """"""
        #grid_tile = html.LI(Class='mdc-grid-tile')
        # return grid_tile

    # ----------------------------------------------------------------------
    # @classmethod
    # def title(self, mdc, text):
        # """"""
        #self['title'].text = text


