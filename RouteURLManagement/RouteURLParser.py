import re

from .Errors import InternalParsingError

class RouteURLParser:
    @staticmethod
    def _generate_regex_for_variable_specifier_type (*, variable_specifier_type):
        if "default" not in variable_specifier_type:
            default = False
        else:
            default = variable_specifier_type ["default"]
        type_name = variable_specifier_type ["type_name"]
        # Returns a regular expression that matches instances of <TYPE:NAME>
        # where TYPE == type_string and NAME is an alphanumeric variable name.
        # If default is set, <NAME> will also be matched by the regex.
        return f"<{type_name}:[^.<>:]+>{'|<[^.<>:]+>' if default else ''}"
    variable_specifier_types = [
        {"type_name": "string", "default": True}, # "default" defaults to False
        {"type_name": "int"}, # "default" is not specified since it defaults to False
        {"type_name": "float"},
        {"type_name": "path"},
        # {"type_name": "uuid"} UUID parsing is disabled due to the added complexity of having a required string length.
    ]
    @staticmethod
    def _get_name_from_variable_specifier_string (*, variable_specifier_string):
        # Argument variable_specifier_string should follow the format <TYPE:NAME> or <NAME>
        # The return value is NAME
        def raise_error (*, reason): raise InternalParsingError (f"Bad variable specifier string {variable_specifier_string}, reason: {reason}")
        if not (variable_specifier_string.startswith ('<') and variable_specifier_string.endswith ('>')):
            raise_error (reason = "missing < and/or >")
        inner_string_part = variable_specifier_string [1:-1] # Removes <> (<TYPE:NAME> --> TYPE:NAME)
        type_and_name_or_name = tuple (inner_string_part.split (':'))
        if not (len (type_and_name_or_name) == 1 or len (type_and_name_or_name) == 2):
            raise_error (reason = "string doesn't follow NAME or TYPE:NAME format")
        if len (type_and_name_or_name) == 2: # ("TYPE", "NAME")
            _type, name = type_and_name_or_name # Expands ("TYPE", "NAME") into _type = "TYPE", name = "NAME"
        else: # ("NAME")
            name = type_and_name_or_name # Expands ("NAME") into name = "NAME"
        return name
    @staticmethod
    def _find_variable_specifiers (*, route_url):
        all_matches = []
        for variable_specifier_type in RouteURLParser.variable_specifier_types:
            regex = RouteURLParser._generate_regex_for_variable_specifier_type (variable_specifier_type = variable_specifier_type)
            matches = list (re.finditer (regex, route_url))
            all_matches += list ({
                "type_name": variable_specifier_type ["type_name"],
                "variable_name": RouteURLParser._get_name_from_variable_specifier_string (
                    variable_specifier_string = match.group ()
                ),
                "re_match": match
            } for match in matches)
        return all_matches
    @staticmethod
    def _segment_route_url_based_on_variable_specifiers (*, route_url, variable_specifiers):
        segments = []
        route_url_position = 0
        # To make sure the target string is parsed from start to end,
        # first the list of variable specifiers is sorted by the lower boundary of each specifier.
        variable_specifiers = sorted (variable_specifiers, key = lambda type_specifier: type_specifier ["re_match"].span () [0])
        for variable_specifier in variable_specifiers:
            string_segment = ""
            lower_boundary = variable_specifier ["re_match"].span () [0]
            while route_url_position < lower_boundary: # While our position in the route URL hasn't caught up to the lower boundary of this variable specifier,
                string_segment += route_url [route_url_position:route_url_position + 1]
                route_url_position += 1
            if string_segment != "": segments.append ({"type": "string", "string": string_segment})
            segments.append ({"type": "variable_specifier", "variable_type": variable_specifier ["type_name"], "variable_name": variable_specifier ["variable_name"]})
            route_url_position = variable_specifier ["re_match"].span () [1]
        if route_url_position <= len (route_url) - 1: # Check if there's a string part after the last variable specifier.
            segments.append ({"type": "string", "string": route_url [route_url_position:]}) # Add this final string part to the list of segments.
        return segments
    @staticmethod
    def parse_route_url (*, route_url):
        # Generate a list of segments -- both strings and variable specifiers --
        # that a URL has to have to match the route URL.
        variable_specifiers = RouteURLParser._find_variable_specifiers (route_url = route_url)
        segments = RouteURLParser._segment_route_url_based_on_variable_specifiers (route_url = route_url, variable_specifiers = variable_specifiers)
        return segments
    def _generate_pretty_segment_printout (*, segments, string_color = "BLUE", variable_specifier_color = "GREEN"): # WARNING: needs Color from utils.py
        from utils import color # utils.py
        out = ""
        print_without_newline = lambda variable: print (variable, end = "")
        for segment in segments:
            if segment ["type"] == "string":
                out += f"{getattr (color, string_color)}{segment ['string']}{color.END}"
            elif segment ["type"] == "variable_specifier":
                out += f"{getattr (color, variable_specifier_color)}<{segment ['variable_type']}:{segment ['variable_name']}>{color.END}"
        return out
