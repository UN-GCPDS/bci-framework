from browser import html, document, timer
import os
import logging


########################################################################
class Stimuli:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, style='original'):
        """"""
        self.style = style
        
        if style == 'original':            
            document.select_one('.bci_stimuli').style = {'background-color': '#000000'}
            
        self.canvas = html.DIV(id='canvas')
        self.score = html.UL(id='score')
        
    # ----------------------------------------------------------------------
    def hide(self):
        """"""
        self.canvas.style = {'background-image': ''}
        
    # ----------------------------------------------------------------------
    def show_target(self, orientation, hide=170):
        """"""
        timer.set_timeout(self.hide, hide)
        self.canvas.style = {'background-image': f'url(/root/assets/{self.style}/target_{orientation.lower()}.png)'}
        
    # ----------------------------------------------------------------------
    def show_fail(self, hide=170):
        """"""
        timer.set_timeout(self.hide, hide)
        self.canvas.style = {'background-image': f'url(/root/assets/{self.style}/fail.png)'}
        self.remove_coin()
        
    # ----------------------------------------------------------------------
    def show_coin(self, hide=170):
        """"""
        timer.set_timeout(self.hide, hide)
        self.canvas.style = {'background-image': f'url(/root/assets/{self.style}/coin.png)'}
        self.score <= html.LI(id='score-coin')      
        
    # ----------------------------------------------------------------------
    def remove_coin(self):
        """"""
        if coin := document.select_one('#score-coin'):
            coin.remove()        
            
    # ----------------------------------------------------------------------
    def add_coin(self):
        """"""
        self.score <= html.LI(id='score-coin')   
        document.select_one('#score-coin').style = {'background-image': f"url('/root/assets/{self.style}/coin.png')"}