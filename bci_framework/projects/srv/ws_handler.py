import json

# import threading
# import socket
import random

# from tornado.httpserver import HTTPServer
from tornado.websocket import WebSocketHandler, WebSocketClosedError
# from tornado.ioloop import IOLoop
# from tornado.web import Application, url  # RequestHandler, StaticFileHandler, Application, url
# import os

# DEBUG = socket.gethostname() == "arch"
# DEBUG = True

clients = []


########################################################################
class WSHandler(WebSocketHandler):
    """"""

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
                    client_g['web'].write_message({'log': 'Device unlinked', })

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


