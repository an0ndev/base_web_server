import http.server, sys, urllib.parse

from ..RouteURLManagement.URLMatcher import URLMatcher

class RequestHandler (http.server.BaseHTTPRequestHandler):
    def __init__ (self, *request_handler_args, web_server_reference, **request_handler_kwargs):
        self.web_server_reference = web_server_reference # Stores a reference to the web server on this object instance.
        # Passes through all arguments and keyword arguments created by the HTTP server class to the call to super ().__init__,
        # which instantiates BaseHTTPRequestHandler using those arguments and keyword arguments.
        super (RequestHandler, self).__init__ (*request_handler_args, **request_handler_kwargs)
    def _handle (self, *, method_name):
        # Do route matching and call the appropriate function
        route_matched = False
        route_list = list ((route_url, route_info) for route_url, route_info in self.web_server_reference.routes.items ())
        # Sort the route list so that the routes marked as priority are handled first
        route_list.sort (
            reverse = True, # Allows routes with priority marked as True (with a sort value of 1) to be forced to the front, with lower list indices
            key = lambda route_tuple: int (route_tuple [1] ["priority"]) # Returns 1 if priority, 0 if not
        )
        path_with_query_string = self.path
        if '?' in path_with_query_string: # Path has a query string
            split_path = path_with_query_string.split ('?')
            path = '?'.join (split_path [:-1])
            self.query_string = split_path [-1]
            parsed_query_string_variables = {}
            query_string_segments = self.query_string.split ('&')
            for query_string_segment in query_string_segments:
                if query_string_segment == '': continue
                variable_name_and_value = query_string_segment.split ('=')
                if len (variable_name_and_value) != 2: continue
                variable_name, variable_value = variable_name_and_value
                variable_name = variable_name.replace ('+', ' ')
                variable_value = urllib.parse.unquote (variable_value) # Replaces "%20" with ' ', etc.
                parsed_query_string_variables [variable_name] = variable_value
            self.args = parsed_query_string_variables
        else: # Path doesn't have a query string
            path = path_with_query_string
            self.args = {}
        for route_url, route_info in route_list:
            match_success, url_variables = URLMatcher.check_url_against_parsed_route_url (url = path, parsed_route_url = route_info ["parsed_route_url"])
            if match_success:
                route_matched = True
                break
        if not route_matched:
            self.send_error (404)
        else:
            if route_info ["pass_reference_to_request_handler"]:
                handler_func_args = [self]
            else:
                handler_func_args = []
            response = route_info ["handler_func"] (*handler_func_args, **url_variables)
            if response is not None:
                response._apply_to (self)
                response._after_completion ()
    def log_message (self, format, *args):
        message = format % args
        if self.web_server_reference.logging_enabled:
            sys.stderr.write (message + "\n")
            sys.stderr.flush ()

# Add functions to RequestHandler for each method name based on a list of method names
# (HTTPServer finds the function to call based on the HTTP method, so we need a function for each HTTP method for maximum compatibility.)
method_names = ["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]
for method_name in method_names:
    setattr (RequestHandler, f"do_{method_name}", lambda self, method_name = method_name: self._handle (method_name = method_name))
