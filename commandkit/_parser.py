""" code by Craig McQueen('How to parse strings to look like sys.argv') """

import sys

_WORD_DIVIDERS = set((' ', '\t', '\r', '\n'))

_QUOTE_CHARS_DICT = {
    '\\':   '\\',
    ' ':    ' ',
    '"':    '"',
    'r':    '\r',
    'n':    '\n',
    't':    '\t',
}

def _raise_type_error():
    raise TypeError("Bytes must be decoded to Unicode first")

def parse_to_argv_gen(instring):
    is_in_quotes = False
    instring_iter = iter(instring)
    join_string = instring[0:0]

    c_list = []
    c = ' '
    while True:
        # Skip whitespace
        try:
            while True:
                if not isinstance(c, str) and sys.version_info[0] >= 3:
                    _raise_type_error()
                if c not in _WORD_DIVIDERS:
                    break
                c = next(instring_iter)
        except StopIteration:
            break
        # Read word
        try:
            while True:
                if not isinstance(c, str) and sys.version_info[0] >= 3:
                    _raise_type_error()
                if not is_in_quotes and c in _WORD_DIVIDERS:
                    break
                if c == '"':
                    is_in_quotes = not is_in_quotes
                    c = None
                elif c == '\\':
                    c = next(instring_iter)
                    c = _QUOTE_CHARS_DICT.get(c)
                if c is not None:
                    c_list.append(c)
                c = next(instring_iter)
            yield join_string.join(c_list)
            c_list = []
        except StopIteration:
            yield join_string.join(c_list)
            break

def parse_to_argv(instring):
    return list(parse_to_argv_gen(instring))