"""
================
Tornado Handlers
================

This handlers are used to configure the `Stimuli Delivery`.
"""

import json
import pickle
import logging
from typing import TypeVar

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from kafka import KafkaProducer

# from datetime import datetime
from bci_framework.extensions import properties as prop

clients = []


JSON = TypeVar('json')


########################################################################
class ModeHandler(RequestHandler):
    """`/mode` endpoint to differentiate between `Data analysis` and `Stimuli Delivery`."""

    # ----------------------------------------------------------------------
    def get(self):
        self.write('stimuli')


########################################################################
class WSHandler(WebSocketHandler):
    """WebSockets is the way to comunicate between dashboard and presentations."""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        super().__init__(*args, **kwargs)

        try:
            self.marker_producer = KafkaProducer(
                bootstrap_servers=[f'{prop.HOST}:9092'],
                compression_type='gzip',
                value_serializer=pickle.dumps
            )
        except:
            logging.warning('Kafka not available!')

    # ----------------------------------------------------------------------
    def check_origin(self, *args, **kwargs):
        """"""
        return True

    # ----------------------------------------------------------------------
    def open(self):
        """"""
        self.print_log('tornado_ok')

    # ----------------------------------------------------------------------
    def on_close(self):
        """"""
        if hasattr(self, 'client_id'):
            print("connection closed: {}".format(self.client_id))

    # ----------------------------------------------------------------------
    def print_log(self, message: str):
        """"""
        try:
            self.write_message({'log': message})
        except Exception as error:
            print(message)
            print(error)
            try:
                self.write_message({'log': error})
            except:
                pass

    # ----------------------------------------------------------------------
    def on_message(self, message: JSON):
        """Input messages are methods reference with arguments.

        The callable are defined with a `bci_` prefix in the methods names.

        Parameters
        ----------
        message
            json string with method name and key words arguments.
        """
        if message:
            data = json.loads(message)
            getattr(self, f'bci_{data["action"]}')(**data)

    # ----------------------------------------------------------------------
    def bci_register(self, **kwargs):
        """Register clients."""
        if not self in clients:
            clients.append(self)
            print('Client added')
        else:
            print('Client already registered')

    # ----------------------------------------------------------------------
    def bci_feed(self, **kwargs):
        """Call the same method in all clients."""
        for i, client in enumerate(clients):
            if client != self:
                try:
                    client.write_message(kwargs)
                except WebSocketClosedError:
                    clients.pop(i)

    # ----------------------------------------------------------------------
    def bci_marker(self, **kwargs):
        """Use kafka to stream markers."""

        marker = kwargs['marker']
        # marker['datetime'] = datetime.now().timestamp()

        if hasattr(self, 'marker_producer'):
            self.marker_producer.send('marker', marker)
        else:
            print("No Kafka produser available!")

    # ----------------------------------------------------------------------
    def bci_annotation(self, **kwargs):
        """Use kafka to stream annotations."""

        annotation = kwargs['annotation']
        # annotation['onset'] = datetime.now().timestamp()

        if hasattr(self, 'marker_producer'):
            self.marker_producer.send('annotation', annotation)
        else:
            print("No Kafka produser available!")
