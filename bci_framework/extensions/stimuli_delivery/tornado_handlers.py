"""
================
Tornado Handlers
================

This handlers are used to configure the `Stimuli Delivery`.
"""

import json
import pickle
import logging
from queue import Queue
from typing import TypeVar
import asyncio

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from kafka import KafkaProducer, KafkaConsumer

from datetime import datetime, timedelta
from bci_framework.extensions import properties as prop
from bci_framework.extensions.data_analysis.utils import thread_this, subprocess_this

created_consumer = [False]
clients = {}
JSON = TypeVar('json')

logging.getLogger('kafka').setLevel(logging.CRITICAL)
logging.getLogger('kafka.conn').setLevel(logging.CRITICAL)


# ----------------------------------------------------------------------
@thread_this
def bci_consumer():
    """"""
    asyncio.set_event_loop(asyncio.new_event_loop())

    try:
        consumer = KafkaConsumer(
            bootstrap_servers=[f'{prop.HOST}:9092'],
            value_deserializer=pickle.loads,
            auto_offset_reset='latest',
        )
    except:
        return

    consumer.subscribe(['feedback'])
    count = 0
    for message in consumer:
        count += 1
        for client in clients:
            try:
                clients[client].write_message(json.dumps({'method': '_on_feedback',
                                                          'args': [],
                                                          'kwargs': {**message.value, **{'c': count, }},
                                                          }))
            except:
                pass


bci_consumer()


########################################################################
class ModeHandler(RequestHandler):
    """`/mode` endpoint to differentiate between `Data analysis` and `Stimuli Delivery`."""

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header("Access-Control-Allow-Headers",
                        "access-control-allow-origin,authorization,content-type")

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
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=[f'{prop.HOST}:9092'],
                compression_type='gzip',
                value_serializer=pickle.dumps,
            )
        except:
            logging.warning(
                f'Kafka host ({prop.HOST}:9092) not available!')

        # self.bci_consumer()

    # ----------------------------------------------------------------------
    def check_origin(self, *args, **kwargs):
        """"""
        return True

    # ----------------------------------------------------------------------
    def open(self):
        """"""
        self.print_log('tornado_ok')

    # # ----------------------------------------------------------------------
    # def on_close(self):
        # """"""
        # if self in clients:
            # clients.pop(clients.index(self))
        # super().on_close(self)

    # # ----------------------------------------------------------------------
    # def on_connection_close(self):
        # """"""
        # if self in clients:
            # clients.pop(clients.index(self))
        # super().on_connection_close(self)

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

            # if data['action'] == 'consumer' and not created_consumer[0]:
                # created_consumer = [True]
                # # bci_consumer()
                # # return
            # elif data['action'] == 'consumer' and created_consumer[0]:
                # return

            getattr(self, f'bci_{data["action"]}')(**data)

    # ----------------------------------------------------------------------
    def bci_register(self, **kwargs):
        """Register clients."""

        clients[kwargs['mode']] = self

    # ----------------------------------------------------------------------
    def bci_feed(self, **kwargs):
        """Call the same method in all clients."""
        # for i, client in enumerate(clients):
            # if client != self:
                # try:
                    # client.write_message(kwargs)
                # except WebSocketClosedError:
                    # clients.pop(i)
        for client in clients:
            if clients[client] != self:
                try:
                    clients[client].write_message(kwargs)
                except:
                    pass

    # ----------------------------------------------------------------------
    def bci_marker(self, **kwargs):
        """Use kafka to stream markers."""

        marker = kwargs['marker']
        marker['datetime'] = (
            datetime.now() - timedelta(milliseconds=marker['latency'] + prop.SYNCLATENCY)).timestamp()
        del marker['latency']
        # marker['datetime'] = datetime.now().timestamp()

        if hasattr(self, 'kafka_producer'):
            self.kafka_producer.send('marker', marker)
        else:
            print("No Kafka produser available!")

    # ----------------------------------------------------------------------
    def bci_annotation(self, **kwargs):
        """Use kafka to stream annotations."""

        annotation = kwargs['annotation']
        annotation['onset'] = (
            datetime.now() - timedelta(milliseconds=annotation['latency'] + prop.SYNCLATENCY)).timestamp()
        del annotation['latency']

        if hasattr(self, 'kafka_producer'):
            self.kafka_producer.send('annotation', annotation)
        else:
            print("No Kafka produser available!")

    # ----------------------------------------------------------------------
    def bci_feedback(self, **kwargs):
        """Use kafka to stream annotations."""

        feedback = kwargs['feedback']

        if hasattr(self, 'kafka_producer'):
            self.kafka_producer.send('feedback', feedback)
        else:
            print("No Kafka produser available!")

    # # ----------------------------------------------------------------------
    # @thread_this
    # def bci_consumer(cls, **kwargs):
        # """"""
        # asyncio.set_event_loop(asyncio.new_event_loop())

        # try:
            # consumer = KafkaConsumer(
                # bootstrap_servers=[f'{prop.HOST}:9092'],
                # value_deserializer=pickle.loads,
                # auto_offset_reset='latest',
            # )
        # except:
            # return

        # consumer.subscribe(['feedback'])
        # count = 0
        # for message in consumer:
            # for client in clients:
                # if cls != clients[client]:
                    # try:
                        # count += 1
                        # clients[client].write_message(json.dumps({'method': '_on_feedback',
                                                                  # 'args': [],
                                                                  # 'kwargs': {**message.value, **{'c': count, }},
                                                                  # }))
                    # except:
                        # pass
                    # # clients.pop(i)


