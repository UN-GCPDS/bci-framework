from bci_framework.projects.server import StimuliServer, StimuliAPI, StimulusInstance
from browser import document, timer, html, window
import mdc


########################################################################
class Widgets(StimuliAPI):

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        document.select('head')[0] <= html.LINK(
            href='/root/styles.css', type='text/css', rel='stylesheet')

        # document <= mdc.MDCButton('Button')
        # document <= mdc.MDCButton('Button raised', raised=True)
        # document <= mdc.MDCButton('Button unelevated', unelevated=True)
        # document <= mdc.MDCButton('Button outlined', outlined=True)

        # document <= mdc.MDCButton(
            # 'Button icon', raised=True, icon='bookmark')
        # document <= mdc.MDCButton(
            # 'Button icon', raised=True, icon='bookmark', reversed=True)
        # document <= mdc.MDCIconToggle(
            # icon_on='star', icon_off='star_outline')

        # document <= mdc.MDCFab(icon='add')
        # document <= mdc.MDCFab(icon='add', label='Add')
        # document <= mdc.MDCFab(icon='add', mini=True)

        form = mdc.MDCForm()
        form.mdc.Radio('Radio button 1', name='r1', checked=True)
        form.mdc.Radio('Radio button 2', name='r1')
        form.mdc.Radio('Radio button 3', name='r1')
        document <= form


if __name__ == '__main__':
    StimuliServer('Widgets')


