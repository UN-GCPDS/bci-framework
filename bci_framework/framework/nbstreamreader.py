"""
==========================
Non blocking stream reader
==========================
"""

import time
from typing import Optional, TypeVar, Union
from threading import Thread
from queue import Queue, Empty


Stdout = TypeVar('Stdout')
Seconds = TypeVar('Seconds')


########################################################################
class NonBlockingStreamReader:
    """Artificial `timeout` for blocking process."""

    # ----------------------------------------------------------------------
    def __init__(self, stream: Stdout):
        """"""
        self.stream_stdout = stream
        self.queue_messages = Queue()
        self.kepp_alive = True

        def _populateQueue(stream, queue):
            """Collect lines from 'stream' and put them in 'quque'."""

            while self.kepp_alive:
                line = stream.readline()
                if line:
                    queue.put(line)
                time.sleep(0.1)

        self.thread_collector = Thread(target=_populateQueue,
                                       args=(self.stream_stdout,
                                             self.queue_messages))
        self.thread_collector.daemon = True
        self.thread_collector.start()  # start collecting lines from the stream

    # ----------------------------------------------------------------------
    def readline(self, timeout: Optional[Seconds] = 0.1) -> Union[str, None]:
        """Read lines from queue object."""
        try:
            return self.queue_messages.get(block=timeout is not None, timeout=timeout)
        except Empty:
            return None

    # ----------------------------------------------------------------------
    def stop(self) -> None:
        """Stop the readline."""
        self.kepp_alive = False
