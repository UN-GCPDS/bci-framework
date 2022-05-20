from radiant import PythonHandler
from matplotlib import pyplot as plt
from io import BytesIO
import base64
import numpy as np
from copy import copy
import logging

status = {}
fig = plt.figure(figsize=(12, 7), dpi=90)
ax = plt.subplot(111)

class BandFeedback(PythonHandler):
    
    
    
    def test_feed(self, bands):
        
        ax.clear()
        ax.plot()
        
        f = BytesIO()
        plt.savefig(f, format='png')
        
        return base64.b64encode(f.getvalue()).decode()
        
    def neurofeedback(self, bands):
    
        ax.clear()
    
        max_ = 10


        for k in bands:
        
            status.setdefault(k, 0)
        
            if bands[k][0] and bands[k][1]=='increase':
                status[k] += 1
            elif not bands[k][0] and bands[k][1]=='increase':
                status[k] -= 1
            elif bands[k][0] and bands[k][1]=='decrease':
                status[k] += 1
            elif not bands[k][0] and bands[k][1]=='decrease':
                status[k] -= 1
    
    
        data = status
    
        bottom = []
        for i in data:
            if data[i]>0:
                bottom.append(1)
            else:
                bottom.append(-1)
    
        bottom = np.array(bottom, dtype=float)
        bottom *= 0.5
    
        for i, (b, name) in enumerate(zip(bottom, bands)):
        
        
        
            # v = status[name]

        
            control = copy(bands[name][1])
            value = bands[name][0]
        
        
            if control=='decrease':
                control = 'increase'
                status[name] = -status[name]

            b=np.sign(status[name])
            b_ = 1
            m = max_
            
            
            if status[name]>max_:
                status[name] = max_
            elif status[name]<-max_:
                status[name] = -max_
        
        
            ax.arrow(i, b_, 0, m, capstyle='projecting', width=0.45, head_width=0.8, head_length=3, fc='w', ls=(0, (10,10)), ec='C0', alpha=0.5, length_includes_head=False)
            if status[name] > 0 and control=='increase' or status[name] < 0 and control=='decrease':
                color='C0'
            else:
                color='C3'
            
            if status[name]:
                ax.arrow(i, b, 0, status[name], capstyle='projecting', width=0.45, head_width=0.8, head_length=3, ec='white', fc=color, length_includes_head=False)
            
            
            ax.text(i, 0, name, ha='center', va='center', fontsize=15)
        

            if bands[name][1]=='decrease':
                # control = 'increase'
                status[name] = -status[name]
    
        ax.set_ylim(-15, 15)
        ax.axis('off')
    
        # fig.savefig('test.png', format='png')
        f = BytesIO()
        fig.savefig(f, format='png')
        
        # logging.warning(f'{status}')
    
        return base64.b64encode(f.getvalue()).decode()