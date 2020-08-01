import copy

from .URLVariableValidator import URLVariableValidator

class URLMatcher:
    @staticmethod
    def check_url_against_parsed_route_url (*, url, parsed_route_url):
        # TODO: Clean up this function... there are lots of dead debug print statements left over. (Eric will take care of this eventually)

        # Note: parsed_route_url is a friendlier name for a list of route URL segments,
        # referred to with the "segments" variable in the RouteURLParser class.
        # In other words, parsed_route_url is analogous to segments.
        parsing_url = copy.deepcopy (url) # Make sure we don't modify the original url passed

        url_variables = {}
        route_url_segment_number = 0
        selection_start = 0
        while route_url_segment_number < len (parsed_route_url):
            # print ("### START OF SEGMENT ITERATION")
            # print (f"### URL VARIABLES: {url_variables}")
            # print (f"### SELECTION PROGRESS: {selection_start}/{len (parsing_url)}")
            # print (f"### REMAINING SELECTION: {parsing_url [selection_start :]}")
            # print (f"### SEGMENT NUMBER: {route_url_segment_number + 1}/{len (parsed_route_url)}")
            current_segment = parsed_route_url [route_url_segment_number]
            # print (current_segment)
            if current_segment ["type"] == "string":
                if parsing_url [selection_start :].startswith (current_segment ["string"]):
                    # print (f"{current_segment ['string']} matches")
                    selection_start += len (current_segment ["string"])
                else:
                    # print (f"{current_segment ['string']} doesn't match")
                    # Get the last segment and check if it's a variable that can yield a character to attempt to make this string match
                    if route_url_segment_number == 0:
                        # This is the first segment and it doesn't match, so the URL doesn't match.
                        return False, None
                    last_segment = parsed_route_url [route_url_segment_number - 1]
                    if last_segment ["type"] != "variable_specifier":
                        # This variable doesn't match and the last segment isn't a variable, so the URL doesn't match.
                        return False, None
                    last_variable = url_variables [last_segment ["variable_name"]]
                    # Check if the last variable contains this string
                    last_variable_index_of_string = last_variable ["value"].find (current_segment ["string"])
                    if last_variable_index_of_string < 0:
                        # The last variable doesn't contain this string. Parsing has failed.
                        return False, None
                    # print ("IT CONTAINS US")
                    # Check the validity of the last variable without this string (and everything after it)
                    sliced_last_variable_value = last_variable ["value"] [: last_variable_index_of_string]
                    # print (sliced_last_variable_value)
                    sliced_last_variable_is_valid = URLVariableValidator.validate_url_variable (
                        _type = last_variable ["type"],
                        url_variable = sliced_last_variable_value
                    ) [0]
                    if not sliced_last_variable_is_valid:
                        # print ("ok we dont got this -- sliced last variable isn't valid")
                        return False, None
                    # print ("THE SLICE IS VALID WE DID IT???")
                    backtrack_amount = len (last_variable ["value"]) - last_variable_index_of_string # The amount we have to move back to line up with the end of the sliced part of the last variable
                    # print (f"Backtracking by {backtrack_amount}")
                    forward_amount = len (current_segment ["string"]) # The amount we have to move forward after finding the current string
                    # print (f"Forward tracking by {forward_amount}")
                    last_variable ["value"] = sliced_last_variable_value # Patch the value of the last variable
                    selection_start -= backtrack_amount
                    selection_start += forward_amount
            elif current_segment ["type"] == "variable_specifier":
                selection_size = 0
                current_selection_matches = True
                finished = False
                while current_selection_matches and not finished:
                    selection_size += 1
                    # print (f"selection size is now {selection_size}")
                    selection = parsing_url [selection_start : (selection_start + selection_size)]
                    # print (f"current selection is {selection}")
                    if selection_size > 1: last_selection_can_yield_character = copy.deepcopy (selection_can_yield_character)
                    current_selection_matches, selection_can_yield_character = URLVariableValidator.validate_url_variable (
                        _type = current_segment ["variable_type"],
                        url_variable = selection
                    )
                    if current_selection_matches:
                        # print (f"iteration: {selection} matches variable {current_segment ['variable_name']} (length: {len (selection)})")
                        # Check if the next iteration will reach the end of the parsing URL
                        if (selection_start + selection_size + 1) > len (parsing_url):
                            # print ("breaking now")
                            url_variables [current_segment ["variable_name"]] = {"type": current_segment ['variable_type'], "value": selection, "can_yield_character": selection_can_yield_character}
                            finished = True
                            selection_start += len (selection)
                    else:
                        selection_size -= 1
                        # print ("Subtracting from selection size")
                        if selection_size > 0:
                            # The attempt to add another character to the selection failed, but the current selection constitutes as a variable,
                            # so just save this selection as a match for the current variable,
                            # and move onto parsing the next segment.
                            selection = parsing_url [selection_start : selection_start + selection_size]
                            # print (f"finished: {selection} matches variable {current_segment ['variable_name']}")
                            url_variables [current_segment ["variable_name"]] = {"type": current_segment ["variable_type"], "value": selection, "can_yield_character": last_selection_can_yield_character}
                            finished = True
                            selection_start += len (selection)
                        else:
                            # The current selection is empty, so see if the last segment is a variable and can yield a character.
                            # print ("got here")
                            if route_url_segment_number == 0:
                                # This is the first segment and it doesn't match, so the URL doesn't match.
                                return False, None
                            last_segment = parsed_route_url [route_url_segment_number - 1]
                            if last_segment ["type"] != "variable_specifier":
                                # This variable doesn't match and the last segment isn't a variable, so the URL doesn't match.
                                return False, None
                            last_variable = url_variables [last_segment ["variable_name"]]
                            last_variable_can_yield_character = last_variable ["can_yield_character"]
                            # TODO: Add functionality to backtrack multiple variables ("iterative backtracking"), e.g. ["test42", "0", (int)] --> ["test4", "2", "0"]
                            if not last_variable_can_yield_character:
                                # print ("ok we dont got this -- last variable cant yield a character")
                                return False, None
                            # print ("WE GOT THIS")
                            last_variable ["value"] = last_variable ["value"] [:-1] # Slice off the last character, since it can be yielded
                            selection_start -= 1 # Move the selection back by one character
                            current_selection_matches = True # Allow another iteration
                            #
#                             if
#
                            # and then check if the result
                            # return False, None
            # print (f"{parsing_url [selection_start:]} left to parse")
            # print (f"(selection_start is now {selection_start})")
            route_url_segment_number += 1
        # print ("We did it???")
        # Make sure there isn't anything left at the end of the original string
        if selection_start < len (parsing_url):
            # print (f"selection_start: {selection_start}, len (parsing_url): {len (parsing_url)}")
            return False, None
        # Post-process URL variables according to their type
        post_processed_url_variables = {}
        for variable_name, variable_info in url_variables.items ():
            variable_value = None
            if variable_info ["type"] == "string":
                variable_value = variable_info ["value"]
            elif variable_info ["type"] == "int":
                variable_value = int (variable_info ["value"])
            elif variable_info ["type"] == "float":
                variable_value = float (variable_info ["value"])
            elif variable_info ["type"] == "path":
                variable_value = variable_info ["value"].split ('/')
            post_processed_url_variables [variable_name] = variable_value
        return True, post_processed_url_variables
