from browser import html, document, timer
import os
import logging


########################################################################
class Stimuli:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, style='original'):
        """"""
        self.canvas = html.DIV(id='rsst-canvas')
        self.score = html.UL(id='rsst-score')
        self.set_style(style)

    # ----------------------------------------------------------------------
    def set_style(self, style):
        """"""
        self.style = style
        if style == 'original':
            document.select_one('.bci_stimuli').style = {
                'background-color': '#000000'}
            if canvas := document.select_one('#rsst-canvas'):
                canvas.style = {'border-color': '#000000'}
        else:
            document.select_one('.bci_stimuli').style = {
                'background-color': '#f5f5f5'}
            if canvas := document.select_one('#rsst-canvas'):
                canvas.style = {'border-color': '#f5f5f5'}

    # ----------------------------------------------------------------------
    def hide(self):
        """"""
        self.canvas.style = {'background-image': ''}

    # ----------------------------------------------------------------------
    def show_target(self, orientation, hide=170):
        """"""
        timer.set_timeout(self.hide, hide)
        self.canvas.style = {
            'background-image': f'url(/root/assets/{self.style}/target_{orientation.lower()}.png)'}

    # ----------------------------------------------------------------------
    def show_fail(self, hide=170):
        """"""
        timer.set_timeout(self.hide, hide)
        self.canvas.style = {
            'background-image': f'url(/root/assets/{self.style}/fail.png)'}
        self.remove_coin()

    # ----------------------------------------------------------------------
    def show_coin(self, hide=170):
        """"""
        timer.set_timeout(self.hide, hide)
        self.canvas.style = {
            'background-image': f'url(/root/assets/{self.style}/coin.png)'}
        # self.score <= html.LI(Class='score-coin')
        self.add_coin()

    # ----------------------------------------------------------------------
    def remove_coin(self):
        """"""
        if coin := document.select_one('.score-coin'):
            coin.remove()

    # ----------------------------------------------------------------------
    def add_coin(self):
        """"""
        coin = html.LI(Class='score-coin')
        self.score <= coin
        coin.style = {'background-image': f'url(/root/assets/{self.style}/coin.png)'}
