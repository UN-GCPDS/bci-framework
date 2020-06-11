import time
import logging

import numpy as np

from bci_framework.projects.figure import FigureStream, subprocess_this, thread_this


from openbci_stream.consumer import OpenBCIConsumer

from scipy.signal import resample

from openbci_stream.preprocess import eeg_features



########################################################################
class Stream():
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """"""

        self.fig = FigureStream(figsize=(16, 9), dpi=60)

        self.axis = self.fig.add_subplot(1, 1, 1)
        xs = np.linspace(0, 5, 500)
        # ys = np.sin(2*np.pi*1*(xs+time.time() / 4))

        ys = np.zeros(xs.shape)

        noise = np.random.normal(size=(16, 500)) * 0.2
        self.lines = [self.axis.plot(xs, ys+i, '-')[0] for i in range(16)]
        # self.axis.set_ylim(0, 1)
        # return self.fig.canvas, lines

        self.stream()



    #----------------------------------------------------------------------
    #@thread_this
    #@subprocess_this
    def stream(self):
        """"""

        # N = 1

        with OpenBCIConsumer() as stream:

            for message in stream:

                data = message.value['data'][0]

#                data = np.mean(data, axis=1)

#                data = resample(data, 100, axis=0)
                # data = data[:, ::50]

                f, Y = eeg_features.welch(data, d=1/250)

                Y = Y / Y.max()
                # N = data.shape[1]

                for i, line in enumerate(self.lines):
                    # y_data = line.get_ydata()
                    # y_data = np.roll(y_data, -N)
                    # y_data[-N:] = i+(data[i]*1)
                    line.set_ydata(Y[i])
                    line.set_xdata(f)

                # self.output.truncate(0)
                # self.output.seek(0)

                self.axis.set_ylim(0, 1)
                self.axis.set_xlim(0, f[-1])

                t0 = time.time()
                self.fig.feed()

                logging.warning('FPS: {:.3f}, Clients: {}, Buffer size: {}'.format(1/(time.time() - t0), self.fig.clients(), self.fig.buffer_size()))

                # fig.print_figure(self.output, format='jpeg')
                # return self.output.getvalue()




if __name__ == '__main__':
    Stream()


# Stream()
