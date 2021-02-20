"""
==========================
Non blocking stream reader
==========================
"""

import time
from typing import Optional
from threading import Thread
from queue import Queue, Empty


########################################################################
class NonBlockingStreamReader:
    """Artificial `timeout` for blocking process.

    Parameters
    ----------
    stream
        The stream to read from, usually a process' stdout or stderr.
    """

    # ----------------------------------------------------------------------
    def __init__(self, stream):
        """"""
        self._s = stream
        self._q = Queue()
        self.running = True

        def _populateQueue(stream, queue):
            '''
            Collect lines from 'stream' and put them in 'quque'.
            '''

            while self.running:
                line = stream.readline()
                if line:
                    queue.put(line)
                # else:
                    # pass
                    # raise UnexpectedEndOfStream
                time.sleep(0.1)

        self._t = Thread(target=_populateQueue, args=(self._s, self._q))
        self._t.daemon = True
        self._t.start()  # start collecting lines from the stream

    # ----------------------------------------------------------------------
    def readline(self, timeout: Optional[int] = 0.1) -> None:
        """Read lines from queue object."""
        try:
            return self._q.get(block=timeout is not None, timeout=timeout)
            # return self._q.get(block=True, timeout=0.1)
        except Empty:
            return None

    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Stop the readline."""
        self.running = False
