from .Server.Server import Server
from .Responses.Response import Response

# Since the package was run from the command line, run a test
server = Server ()
@server.route ("/<string:input_string>", pass_reference_to_request_handler = True)
def root (request_handler, input_string):
    response_text = f"Success! You said '{input_string}'."
    return Response.init_with_text (text = response_text)
@server.route ("/shutdown", priority = True, pass_reference_to_request_handler = True) # Setting priority forces this route to be checked before non-priority routes (e.g. root)
def shutdown (request_handler):
    # after_completion_func allows us to provide a function to be called once the request completes.
    # This is especially useful in situations such as this one,
    # where trying to shut down the server before the request completes would cause the shut down operation to wait for the request to complete,
    # creating a deadlock.
    return Response.init_with_text (text = "Shutting down...", after_completion_func = server.shutdown)
print ("Running the server")
server.run ()
print ("Done")
