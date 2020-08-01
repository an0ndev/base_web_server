import string

class URLVariableValidator: # This class is used internally by URLMatcher. The inclusion of a "yieldable character check" in each validator is superfluous and will be cleaned up in the future.
    @staticmethod
    def validate_url_variable (*, url_variable, _type): # Offloads the validation of the URL variable to another function based on its type
        if _type not in URLVariableValidator.validators.keys ():
            raise InternalParsingError (f"Validation of URL variable type {_type} is unimplemented")
        return URLVariableValidator.validators [_type] (url_variable = url_variable)
    @staticmethod
    def string_validator (*, url_variable, _skip_yieldable_character_check = False):
        if len (url_variable) == 0: return False if _skip_yieldable_character_check else (False, False)
        is_valid = True
        for character in url_variable:
            # if character not in string.ascii_letters + string.digits:
            if character == '/': # "accepts any text without a slash" from https://flask.palletsprojects.com/en/1.1.x/quickstart/#variable-rules
                is_valid = False
        if _skip_yieldable_character_check:
            return is_valid
        else:
            can_yield_character = URLVariableValidator.string_validator (
                url_variable = url_variable [:-1], _skip_yieldable_character_check = True
            )
            return is_valid, is_valid and can_yield_character
    @staticmethod
    def int_validator (*, url_variable, _skip_yieldable_character_check = False):
        if len (url_variable) == 0: return False if _skip_yieldable_character_check else (False, False)
        is_valid = True
        for character in url_variable:
            if character not in string.digits:
                is_valid = False
        if _skip_yieldable_character_check:
            return is_valid
        else:
            can_yield_character = URLVariableValidator.int_validator (
                url_variable = url_variable [:-1], _skip_yieldable_character_check = True
            )
            return is_valid, is_valid and can_yield_character
    @staticmethod
    def float_validator (*, url_variable, _skip_yieldable_character_check = False):
        if len (url_variable) == 0: return False if _skip_yieldable_character_check else (False, False)
        if url_variable.count ('.') != 1: return False, False
        left_side, right_side = tuple (url_variable.split ('.'))
        left_side_valid = URLVariableValidator.int_validator (url_variable = left_side, _skip_yieldable_character_check = True)
        if _skip_yieldable_character_check:
            right_side_valid = URLVariableValidator.int_validator (url_variable = right_side, _skip_yieldable_character_check = True)
            return left_side_valid and right_side_valid
        else:
            right_side_valid, right_side_can_yield_character = URLVariableValidator.int_validator (url_variable = right_side)
            return left_side_valid and right_side_valid, left_side_valid and right_side_valid and right_side_can_yield_character
    @staticmethod
    def path_validator (*, url_variable, _skip_yieldable_character_check = False):
        if len (url_variable) == 0: return False if _skip_yieldable_character_check else (False, False)
        is_valid = True
        # From https://flask.palletsprojects.com/en/1.1.x/quickstart/#variable-rules
        # string: "accepts any text without a slash"
        # path: like string but also accepts slashes
        # Because of this, we don't need to check anything except the length
        # and then just return True in the correct format based on whether or not we're skipping the character check
        # (Also, we can't yield a character if there's only one character in the path)
        return True if _skip_yieldable_character_check else (True, len (url_variable) == 1)
    validators = { # These have to be defined using __func__ to access the function part of the static methods: see https://stackoverflow.com/a/41921291/5037905
        "string": string_validator.__func__,
        "int": int_validator.__func__,
        "float": float_validator.__func__,
        "path": path_validator.__func__
    }
