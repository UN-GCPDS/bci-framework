from browser import html, document, timer
import os
import logging

########################################################################
class Stimuli:
    """"""

    # ----------------------------------------------------------------------
    def __init__(self):
        """"""
        # self.coin = os.path.join('assets', 'coin.png')
        # self.coin_plus = os.path.join('assets', 'coin_plus.png')
        # self.goomba = os.path.join('assets', 'goomba.png')
        # self.target = os.path.join('assets', 'target_.png')
        
        
        self.canvas = html.DIV(id='canvas')
        
        self.score = html.UL(id='score')
        
        
        
    # ----------------------------------------------------------------------
    def hide(self):
        """"""
        self.canvas.style = {'background-image': ''}
        
    # ----------------------------------------------------------------------
    def show_target(self, orientation):
        """"""
        self.canvas.style = {'background-image': f'url(/root/assets/target_{orientation.lower()}.png)'}
        
    # ----------------------------------------------------------------------
    def show_goomba(self):
        """"""
        self.canvas.style = {'background-image': 'url(/root/assets/goomba.png)'}
        
    # ----------------------------------------------------------------------
    def show_coin(self):
        """"""
        timer.set_timeout(self.hide, 300)
        self.canvas.style = {'background-image': 'url(/root/assets/coin.png)'}
        self.score <= html.LI(id='score-coin')   
        logging.warning('Coin')    
        
    # ----------------------------------------------------------------------
    def remove_coin(self):
        """"""
        if coin := document.select_one('#score-coin'):
            coin.remove()        
            
    # ----------------------------------------------------------------------
    def add_coin(self):
        """"""
        self.score <= html.LI(id='score-coin')   