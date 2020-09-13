"""
Brython MDCComponent: MDCShape
==============================


"""

from .core import MDCTemplate
#from .MDCButton import MDCButton,  MDCIconToggle


########################################################################
class MDCShape(MDCTemplate):
    """"""

    NAME = 'shape', 'MDCShape'

    CSS_classes = {

        #'_16_9': 'mdc-card__media--16-9',
        #'square': 'mdc-card__media--square',
    }

    MDC_optionals = {

        #'outlined': 'mdc-card--outlined',
        #'full_bleed': 'mdc-card__actions--full-bleed',
        #'icon': '<i class="material-icons mdc-button__icon" aria-hidden="true">{icon}</i>',
        #'disabled': 'disabled',

    }

    #----------------------------------------------------------------------
    def __new__(self, component, **kwargs):
        """"""
        #component = component
        self.element = self.render(locals(), kwargs)

        self.element <= component

        return self.element



    #----------------------------------------------------------------------
    @classmethod
    def __html__(cls, **context):
        """"""

        #context['component'] = context['component'].html

        #cls.ID = cls.new_id()
        #context['id'] = cls.ID

        code = """
            <div class="mdc-shape-container">
                <div class="mdc-shape-container__corner mdc-shape-angled-corner mdc-shape-container__corner--top-left"></div>
                <div class="mdc-shape-container__corner mdc-shape-container__corner--top-right"></div>
                <div class="mdc-shape-container__corner mdc-shape-container__corner--bottom-right"></div>
                <div class="mdc-shape-container__corner mdc-shape-container__corner--bottom-left"></div>
              </div>
        """



        return cls.render_html(code, context)


    #----------------------------------------------------------------------
    @classmethod
    def set_corners(cls, element, background_color='unset', outlined=False, size=None, outline_width='2px', outline_style='solid', outline_color='unset'):
        """"""

        if not isinstance(size, (list, tuple)):
            args = size, size, size, size,
        else:
            args = size

        if len(args) > 1:
            top_left_size, top_right_size, bottom_right_size, bottom_left_size = args
        else:
            top_left_size, top_right_size, bottom_right_size, bottom_left_size = args[0], args[0], args[0], args[0]

        corners = (
            ('top', 'left', top_left_size),
            ('top', 'right', top_right_size),
            ('bottom', 'right', bottom_right_size),
            ('bottom', 'left', bottom_left_size),
        )

        for x, y, size in corners:

            diagonal_length = 'calc({} * 1.4142135623730951)'.format(size)
            diagonal_length_2 = 'calc({} * -1.4142135623730951 / 2)'.format(size)

            corner = cls.element.select('.mdc-shape-container__corner--{}-{}'.format(x, y))[0]

            corner.style = {
                '{}'.format(y): diagonal_length_2,
                '{}'.format(x): diagonal_length_2,
                'width': diagonal_length,
                'height': diagonal_length,
                'background-color': background_color,
            }


        if outlined:

            for shape in cls.element.select('.mdc-shape-container__corner'):
                shape.style = {
                    #'top': outline_width,
                    'border-bottom': '{} {} {}'.format(outline_width, outline_style, outline_color),
                }


    #@mixin mdc-shape-angled-corner-outline($outline-width, $outline-color, $outline-style: solid) {
      #.mdc-shape-container__corner::before {
        #top: $outline-width;
        #border-bottom: $outline-width $outline-style $outline-color;
      #}
    #}




        #@each $y, $x, $size in $corners {
          #@if $size > 0 {
            #// Assume that the size passed represents the width/height rather than the diagonal.
            #// This makes it trivial e.g. to accomplish a horizontal arrow cap by specifying exactly half the shape's height.
            #// Unfortunately, Sass doesn't have built-in exponentiation, and node-sass custom functions seem to hang.
            #// (https://github.com/sass/node-sass/issues/857 may be related, but the workaround didn't seem to work.)
            #// Fortunately, if we assume 45 degree cutouts all the time, a^2 + b^2 = c^2 simplifies to a*sqrt(2).
            #$diagonal-length: $size * 1.4142135623730951;

            #.mdc-shape-container__corner--#{$y}-#{$x} {
              ##{$y}: -$diagonal-length / 2;
              ##{$x}: -$diagonal-length / 2;
              #width: $diagonal-length;
              #height: $diagonal-length;
            #}
          #}
        #}


    #----------------------------------------------------------------------
    @classmethod
    def __getitem__(self, name):
        """"""
        #if name is 'actions':
            #return self.element.select('.mdc-card__actions')[0]

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


