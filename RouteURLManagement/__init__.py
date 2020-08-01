# This package provides classes with methods to parse route URLs (e.g. "/api/v2/<string:api_endpoint>"),
# check URLs (e.g. "/api/v2/test") against those parsed route URLs,
# and extract URL variables (e.g. "test") from a URL that matches a route URL.
# It isn't perfect but it covers most basic use cases, with only one known badly handled edge case, which is documented here.

# KNOWN ISSUE: This route URL and URL pair still fails to match, while Flask/Werkzeug handles it """fine""". (The parser doesn't fail, that is.)
# See the TODO about "iterative backtracking".
# It shouldn't matter anyway; having multiple variables directly adjacent is an edge case that shouldn't exist in practice.
# There isn't any logical reason to have multiple integers next to each other without a separator; even if they are parsed to be valid,
# the developer has no way of knowing where the separator between the integers was supposed to go.
# route_url = "/front_segment/<string:front_string>/<string:string_with_ints><int:int_one><int:int_two>/<path:middle_path>/middle_segment/<string:last_variable>"
# url = "/front_segment/front_string/test420/middle/path/here/middle_segment/last_variable_value"
