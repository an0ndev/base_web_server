from .RouteURLParser import RouteURLParser
from .URLVariableValidator import URLVariableValidator
from .URLMatcher import URLMatcher

# Since the package was run from the command line, run a test given a mode provided by the user
mode = input ("Mode (r --> route URL parser, u --> URL variable validator, m --> URL matcher): ")
if mode == "r":
    route_url = input ("Type a route URL to parse: ")
    segments = RouteURLParser.parse_route_url (route_url = route_url)
    print (RouteURLParser._generate_pretty_segment_printout (segments = segments))
    variable_specifier_list_string = "; ".join (f"type: {segment ['variable_type']}, name: {segment ['variable_name']}" for segment in segments if segment ["type"] == "variable_specifier")
    print (f"Variable specifiers: {variable_specifier_list_string}")
elif mode == "u":
    _type = input ("Type (string/int/path/float): ")
    url_variable = input ("URL variable contents: ")
    is_valid, can_yield_character = URLVariableValidator.validate_url_variable (
        _type = _type,
        url_variable = url_variable
    )
    print (f"Is valid: {is_valid}, can yield character: {can_yield_character}")
elif mode == "m":
    route_url = input ("Type a route URL to parse: ")
    print (f"Parsing route URL {route_url}")
    parsed_route_url = RouteURLParser.parse_route_url (route_url = route_url)
    url = input ("Type a URL to check against the route URL: ")
    print (f"Checking URL {url}")
    parse_success, parsed_variables = URLMatcher.check_url_against_parsed_route_url (url = url, parsed_route_url = parsed_route_url)
    print (f"Parse success: {parse_success}")
    if parse_success: print (f"Parsed variables: {parsed_variables}")
else:
    print ("Invalid mode!")
