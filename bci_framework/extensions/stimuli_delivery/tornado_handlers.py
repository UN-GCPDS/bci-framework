import json
import pickle
import logging

from tornado.web import RequestHandler
from tornado.websocket import WebSocketHandler, WebSocketClosedError
from kafka import KafkaProducer

# from datetime import datetime
from bci_framework.extensions import properties as prop

clients = []


########################################################################
class ModeHandler(RequestHandler):
    """"""

    # ----------------------------------------------------------------------
    def get(self):
        self.write('stimuli')


########################################################################
class WSHandler(WebSocketHandler):
    """"""

    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        """"""
        try:
            self.marker_producer = KafkaProducer(
                bootstrap_servers=[f'{prop.HOST}:9092'],
                compression_type='gzip',
                value_serializer=pickle.dumps
            )
        except:
            logging.warning('Kafka not available!')
        super().__init__(*args, **kwargs)

    # ----------------------------------------------------------------------
    def check_origin(self, origin):
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
            # if DEBUG:
            print("connection closed: {}".format(self.client_id))

            if self.client_id in clients:
                client_g = clients[self.client_id]

                if self == client_g['web']:
                    client_g['web'] = None
                    print('Clossed: web')

                elif self == client_g['device']:
                    client_g['device'] = None
                    print('Clossed: device')
                    client_g['web'].write_message(
                        {'log': 'Device unlinked', })

    # ----------------------------------------------------------------------
    def print_log(self, message):
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
    def on_message(self, message):
        """"""
        if message:
            data = json.loads(message)
            getattr(self, 'bci_{action}'.format(**data))(**data)

    # ----------------------------------------------------------------------
    def bci_register(self, **kwargs):
        """"""
        if not self in clients:
            clients.append(self)
            print('Client added')
        print('Client already registered')

    # ----------------------------------------------------------------------
    def bci_feed(self, **kwargs):
        """"""
        for i, client in enumerate(clients):
            if client != self:
                try:
                    client.write_message(kwargs)
                except WebSocketClosedError:
                    clients.pop(i)

    # ----------------------------------------------------------------------
    def bci_marker(self, **kwargs):
        """"""
        marker = kwargs['marker']
        # marker['datetime'] = datetime.now().timestamp()

        if hasattr(self, 'marker_producer'):
            self.marker_producer.send('marker', marker)
        else:
            print("No Kafka produser available!")

    # ----------------------------------------------------------------------
    def bci_annotation(self, **kwargs):
        """"""
        annotation = kwargs['annotation']
        # annotation['onset'] = datetime.now().timestamp()

        if hasattr(self, 'marker_producer'):
            self.marker_producer.send('annotation', annotation)
        else:
            print("No Kafka produser available!")
