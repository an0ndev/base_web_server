from .Errors import ResponseCreationError

class Response:
    def __init__ (self, *, response_code = 200, headers = {}, body = b"", from_code = False, after_completion_func = None):
        if not from_code:
            raise ResponseCreationError ("__init__ should only be called internally! Call one of the init_with functions instead.")
        self.response_code = response_code
        self.headers = headers
        self.body = body
        self.after_completion_func = after_completion_func
    def _apply_to (self, request_handler):
        request_handler.send_response (self.response_code)
        for header_name, header_value in self.headers.items ():
            request_handler.send_header (header_name, header_value)
        request_handler.send_header ("Content-Length", str (len (self.body)))
        request_handler.end_headers ()
        request_handler.wfile.write (self.body)
        request_handler.wfile.write (b"\r\n\r\n") # Finalizes the response. The client should close the connection after receiving this.
    def _after_completion (self): # This should be called after the response is applied to a request handler.
        if self.after_completion_func is not None:
            self.after_completion_func ()
    @staticmethod
    def init_with_text (*, text, content_type = "text/plain; charset=UTF-8", **kwargs):
        return Response (
            headers = {"Content-Type": content_type},
            body = text.encode (),
            from_code = True,
            **kwargs
        )
    @staticmethod
    def init_with_json (*, data, **kwargs):
        data_as_json = json.dumps (data)
        return Response.init_with_text (text = data_as_json, content_type = "application/json; charset=UTF-8", **kwargs)
