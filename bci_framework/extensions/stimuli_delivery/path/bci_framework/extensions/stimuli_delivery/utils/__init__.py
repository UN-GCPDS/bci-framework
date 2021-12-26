from .widgets import Widgets as w
from radiant.sound import Tone as t
from .units import Units
from browser import html, document, timer

Widgets = w()
Tone = t()


# ----------------------------------------------------------------------
def keypress(callback, timeout=3000):
    """"""
    [h.remove() for h in document.select('.hidden-input')]
    capture_key = html.INPUT(type="text", name="capture", Class='hidden-input', value="", style={
                             'position': 'absolute', 'opacity': 0, 'top': 0})
    document <= capture_key
    capture_key.focus()

    def process(key=None):
        callback(key)
        if timeout:
            timer.clear_timeout(t)
        capture_key.unbind('keypress')
        capture_key.remove()

    def handle(evt):
        key = chr(evt.charCode)
        process(key)

    capture_key.bind('keypress', handle)
    if timeout:
        t = timer.set_timeout(process, timeout)
