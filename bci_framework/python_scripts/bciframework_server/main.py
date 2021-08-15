import os
from radiant.server import RadiantAPI, RadiantServer
from browser import document, html, window, timer, ajax

from mdc.MDCComponent import MDCComponent


########################################################################
class BareMinimum(RadiantAPI):

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)
        self.add_css_file('styles.css')
        document.select_one('body') <= html.TITLE(
            'BCI-Framework | Stimuli Delivery Server')

        self.current_stimuli_url = self.LocalInterpreter.get_url()
        document.select_one('body') <= html.IFRAME(Class='stimuli-delivery',
                                                   src=self.current_stimuli_url)
        timer.set_interval(self.ping, 5000)

    # ----------------------------------------------------------------------
    def on_ping(self, req):
        """"""
        if req.status != 200:
            url = self.LocalInterpreter.get_url()
            if self.current_stimuli_url != url:
                self.current_stimuli_url = url
                window.location.reload()
            else:
                self.stand_by()

    # ----------------------------------------------------------------------
    def ping(self):
        """"""
        url = f'{self.current_stimuli_url}/mode'
        req = ajax.Ajax()
        req.bind("complete", self.on_ping)
        req.set_timeout(500)
        req.open('GET', url, True)
        req.send()

    # ----------------------------------------------------------------------
    def stand_by(self):
        """"""
        document.select_one('body').clear()
        document.select_one('body') <= html.TITLE(
            'BCI-Framework | Stimuli Delivery Server')

        label = MDCComponent(html.SPAN(f'BCI-Framework', Class='bcif-title'))
        label.mdc.typography('headline1')
        label2 = MDCComponent(
            html.SPAN(f'Stimuli Delivery Server', Class='bcif-tag'))
        label2.mdc.typography('subtitle1')

        content = html.DIV(Class='bcif-content')
        content <= label
        content <= html.BR()
        content <= label2

        document.select_one('body') <= content


if __name__ == '__main__':
    RadiantServer('BareMinimum',
                  python=(os.path.join(os.path.dirname(os.path.abspath(
                      __file__)), 'local.py'), 'LocalInterpreter'),
                  host='0.0.0.0',
                  port=9999,
                  brython_version='3.9.5',
                  debug_level=0
                  )


