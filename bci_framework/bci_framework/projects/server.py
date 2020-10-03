from tornado.web import Application, url, RequestHandler, StaticFileHandler
from tornado.ioloop import IOLoop
from tornado.httpserver import HTTPServer
from functools import wraps

import random
import sys
import os

from .srv.ws_handler import WSHandler

StimuliAPI = object
DEBUG = True

if len(sys.argv) > 1:
    port = sys.argv[1]
else:
    port = '5000'
# port = '5000'


########################################################################
class DeliveryInstance_:
    """"""

    # ----------------------------------------------------------------------
    @classmethod
    def both(cls, method):
        def wrap(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except:
                return method()
        return wrap

    # ----------------------------------------------------------------------
    @classmethod
    def remote(cls, method):
        def wrap(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except:
                return method()
        return wrap

    # ----------------------------------------------------------------------

    @classmethod
    def local(cls, method):
        def wrap(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except:
                return method()
        return wrap

    # # ----------------------------------------------------------------------
    # @classmethod
    # def propagate(cls, *arguments):
        # def inner_function(method):
            # @wraps(method)
            # def wrap(*args, **kwargs):
                # try:
                    # return method(*args, **kwargs)
                # except:
                    # return method()
            # return wrap
        # return inner_function


DeliveryInstance = DeliveryInstance_()


########################################################################
class DashboardHandler(RequestHandler):
    def get(self):
        class_ = self.settings['class']
        module = self.settings['module']
        port = self.settings['port']
        seed = self.settings['seed']
        mode = 'dashboard'

        variables = locals().copy()
        variables.pop('self')
        self.render("srv/templates/index.html", **variables)


# ########################################################################
# class DevelopmentHandler(RequestHandler):
    # def get(self):
        # class_ = self.settings['class']
        # module = self.settings['module']
        # port = self.settings['port']
        # seed = self.settings['seed']
        # mode = 'development'

        # variables = locals().copy()
        # variables.pop('self')
        # self.render("srv/templates/index.html", **variables)


########################################################################
class StimuliHandler(RequestHandler):
    def get(self):
        class_ = self.settings['class']
        module = self.settings['module']
        port = self.settings['port']
        seed = self.settings['seed']
        mode = 'stimuli'

        variables = locals().copy()
        variables.pop('self')
        self.render("srv/templates/index.html", **variables)


########################################################################
class ModeHandler(RequestHandler):
    def get(self):
        self.write('stimuli')


# ----------------------------------------------------------------------
def make_app(class_):

    settings = {
        "debug": DEBUG,
        'static_path': os.path.join(os.path.dirname(__file__), 'srv', 'static'),
        'static_url_prefix': '/static/',
        "xsrf_cookies": False,
        'class': class_,
        'module': os.path.split(sys.path[0])[-1],
        'port': port,
        'autoreload': False,
        'seed': random.randint(0, 1000),
    }

    return Application([

        url(r'^/$', StimuliHandler),
        url(r'^/delivery', DashboardHandler),  # GUI
        # url(r'^/development', DevelopmentHandler),
        url(r'^/mode', ModeHandler),
        url(r'^/root/(.*)', StaticFileHandler, {'path': sys.path[0]}),
        url(r'^/ws', WSHandler),

    ], **settings)


# ----------------------------------------------------------------------
def StimuliServer(class_):
    """"""
    print("Stimuli Delivery running on port {}".format(port))
    application = make_app(class_)
    http_server = HTTPServer(application)
    http_server.listen(port, '0.0.0.0')
    IOLoop.instance().start()

