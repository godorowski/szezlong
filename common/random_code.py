import math
from random import choice

CHARS = '23456789abcdefghijkmnrstuvwxyz'
CHARS_LEN = len(CHARS)


def get_code(length=None, count=None):
    if count is not None:
        length = code_len(count)
    return "".join([choice(CHARS) for i in range(length)])


def code_len(count):
    count = max(count, CHARS_LEN + 1)
    return int(math.log(count, CHARS_LEN)) + 1
