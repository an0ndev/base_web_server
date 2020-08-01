import http.server
import threading

from .Errors import NewRouteError

from ..Requests.RequestHandler import RequestHandler

from ..RouteURLManagement.RouteURLParser import RouteURLParser

class Server:
    def __init__ (self, host = "0.0.0.0", port = 5000, server_class = http.server.ThreadingHTTPServer, logging_enabled = True):
        self.logging_enabled = logging_enabled
        self.routes = {}
        def request_handler_generator (*request_handler_args, **request_handler_kwargs):
            return RequestHandler ( # Instantiates a new instance of the request handler,
                *request_handler_args, # passing through any arguments created by the HTTP server class,
                web_server_reference = self, # adding our own custom keyword argument that contains a reference to this web server,
                **request_handler_kwargs # and passing through any keyword arguments created by the HTTP server class.
            )
        self.httpd = server_class ((host, port), request_handler_generator)
    def route (self, route_url, overwrite = False, priority = False, pass_reference_to_request_handler = False): # Generates a function that gets passed a URL handler. Handy for @app.route (url)
        def route_generator (handler_func):
            if route_url in self.routes and not overwrite:
                raise NewRouteError (f"Duplicate route: {route_url}, set overwrite in the decorator to overwrite")
            parsed_route_url = RouteURLParser.parse_route_url (route_url = route_url)
            self.routes [route_url] = {"parsed_route_url": parsed_route_url, "handler_func": handler_func, "priority": priority, "pass_reference_to_request_handler": pass_reference_to_request_handler}
        return route_generator
    def run (self, threaded = False, daemon = True):
        if threaded:
            self._run_thread = threading.Thread (target = self.httpd.serve_forever, daemon = daemon)
            self._run_thread.start ()
        else:
            self.httpd.serve_forever ()
    def shutdown (self, threaded = False, daemon = True):
        if threaded:
            self._shut_down_thread = threading.Thread (target = self.httpd.shutdown, daemon = daemon)
            self._shut_down_thread.start ()
        else:
            self.httpd.shutdown ()
