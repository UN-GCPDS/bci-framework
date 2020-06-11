import time
import logging

import numpy as np

from bci_framework.projects.figure import FigureStream, subprocess_this, thread_this


from openbci_stream.consumer import OpenBCIConsumer


import mne
logger = logging.getLogger("mne")
logger.setLevel(logging.CRITICAL)



########################################################################
class Stream():
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """"""

        self.fig = FigureStream(figsize=(16, 9), dpi=60)

        self.axis = self.fig.add_subplot(1, 1, 1)
        # xs = np.linspace(0, 5, 500)
        # # ys = np.sin(2*np.pi*1*(xs+time.time() / 4))

        # ys = np.zeros(xs.shape)

        # noise = np.random.normal(size=(16, 500)) * 0.2
        # self.lines = [self.axis.plot(xs, ys+i, '-')[0] for i in range(16)]
        # self.axis.set_ylim(0, 16)
        # return self.fig.canvas, lines

        self.stream()



    #----------------------------------------------------------------------
    #@thread_this
    #@subprocess_this
    def stream(self):
        """"""

        name = 'standard_1020'
        channels_names = 'Fp1,Fp2,F7,Fz,F8,C3,Cz,C4,T5,P3,Pz,P4,T6,O1,Oz,O2'.split(',')
        info = mne.create_info(channels_names, sfreq=1000, ch_types="eeg", montage=name)

        with OpenBCIConsumer() as stream:

            for message in stream:

                data = message.value['data'][0]

                data = data - np.mean(data, axis=0)

#                data = resample(data, 100, axis=0)
                # data = data[:, ::50]

                self.axis.clear()
                im, c = mne.viz.plot_topomap(data.mean(axis=1), info, axes=self.axis, show=False, outlines='skirt')


                # self.output.truncate(0)
                # self.output.seek(0)

                # self.fig.show()

                t0 = time.time()
                self.fig.feed()

                logging.warning('FPS: {:.3f}, Clients: {}, Buffer size: {}'.format(1/(time.time() - t0), self.fig.clients(), self.fig.buffer_size()))

                # fig.print_figure(self.output, format='jpeg')
                # return self.output.getvalue()




if __name__ == '__main__':
    Stream()


# Stream()
