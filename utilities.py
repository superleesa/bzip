__author__ = "Satoshi Kashima"
__sid__ = 32678940


import random

MIN_ASCII, MAX_ASCII = 37, 126


def hash_char(char: str) -> int:
    assert MIN_ASCII <= ord(char) <= MAX_ASCII or char == "$", "all characters must be in ascii value of 37-126, or '$'"

    if char == "$":
        return 0
    else:
        return ord(char) - MIN_ASCII + 1

def hash_back_tochar(idx) -> str:
    if idx == 0:
        return "$"
    else:
        return chr(idx + MIN_ASCII - 1)

def hash_char_from_ascii(char_ascii: int):
    assert MIN_ASCII <= char_ascii <= MAX_ASCII or char_ascii == ord("$"), "all characters must be in ascii value of 37-126, or '$'"

    if char_ascii == ord("$"):
        return 0
    else:
        return char_ascii - MIN_ASCII + 1

def generate_random_string():
    length = random.randint(1, 50)
    ascii_range = (MIN_ASCII, MAX_ASCII)
    return ''.join(chr(random.randint(*ascii_range)) for _ in range(length))
