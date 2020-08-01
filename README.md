# Base Web Server
A super lightweight, easy-to-use HTTP server for Python 3 with zero non-builtin dependencies and a five-line hello world:

```python
import base_web_server # Import the module containing everything
server = base_web_server.Server.Server.Server () # Initialize the server
@server.route ("/") # Specify that this function should handle HTTP calls to /
def root (): # Create a handler function with no arguments
    return base_web_server.Responses.Response.Response.init_with_text (
        text = "Hello, world!" # Return a new response with the text "Hello, world!"
    )
server.run (host = "localhost", port = 5000) # Run the server, specifying a host and port
# Test it out by visiting localhost:5000 in a browser!
```

Requires Python >=3.7. (Built and tested on 3.7.3)

## Related projects
These awesome open-source projects use this module. Check them out, or open an issue in this repository to get your project added to the list.
- [connervieira/HealthBox](https://github.com/connervieira/HealthBox): An open source platform to centralize health information

## Reporting bugs/feature requests
Please open an issue in this repository. Thanks so much! -E
