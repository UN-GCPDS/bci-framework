from .widgets import Widgets as w
from radiant.sound import Tone as t
from .units import Units
from browser import html, document, timer

Widgets = w()
Tone = t()


# ----------------------------------------------------------------------
def keypress(callback, timeout=3000):
    """"""
    capture_key = html.INPUT(type="text", name="capture", value="", style={
                             'position': 'absolute', 'opacity': 0})
    document <= capture_key
    capture_key.focus()

    def remove():
        capture_key.unbind('keypress')
        capture_key.remove()
        print('removed')

    def handle(evt):
        key = chr(evt.charCode)
        callback(key)
        remove()

    capture_key.bind('keypress', handle)
    if timeout:
        timer.set_timeout(remove, timeout)
