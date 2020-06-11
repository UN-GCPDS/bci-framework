from bci_framework.projects.server import StimuliServer
from browser import document, console, timer, html
import random


# "from browser import document, console, timer, html"
# 'from browser import document, console, timer, html'

# 'width'jkhjk'100vw'
# "width"jkhjk"100vw"

value="&#x1f83a;", #checked=True
value="&#x1f83a;", checked=True

value='&#x1f83a;', #checked=True
value='&#x1f83a;', checked=True


class Arrows:

    def __init__(self):
        """"""

        self.right = '&#x1f83a;'
        self.left = '&#x1f838;'

        document.select('head')[0] <= html.LINK(href='/root/styles.css', type='text/css', rel='stylesheet')

        self.container = html.DIV()

        document <= self.container

        self.hint = html.SPAN(self.right)

        self.container <= self.hint
        # self.container.style = {'text-align': 'center',
                           # 'margin-top': '50vh',
                           # 'background-color': 'black',
                           # 'width': '100vw',
                           # 'height': '100vh',
                           # }

        self.hint.style = {'font-size': '400px',
                           'color': '#4dd0e1',
                           }

        timer.set_interval(self.show_hint, 1000)

    def show_hint(self):

        h = random.choice([self.right, self.left])
        self.hint.html = h
        # print(h)
        # self.container.style = {'text-align': 'center',
                           # 'margin-top': '50vh',
                           # 'background-color': 'black',
                           # 'width': '100vw',
                           # 'height': '100vh',
                           # }


if __name__ == '__main__':
    StimuliServer('Arrows')
 
