__author__ = "Satoshi Kashima"
__sid__ = 32678940
__description__ = "The implementation of BWT encoder and decoder"

from typing import Optional
from utilities import hash_char
from st2sa import suffix_array as get_suffix_array

MIN_ASCII, MAX_ASCII = 37, 126

def bwt_encode_with_ukkonen(text: str) -> str:
    suffix_array = get_suffix_array(text)

    last_items = [None]*len(suffix_array)

    for i, index in enumerate(suffix_array):
        last_item_index = (index-1 + len(suffix_array)-1) % len(suffix_array)
        last_items[i] = text[last_item_index] if last_item_index != len(suffix_array)-1 else "$"

    return "".join(last_items)


def bwt_encode_naive(text: str) -> str:
    """
    A naive implementation of bwt encoder.
    """

    # create circular suffixes
    text = text + "$"
    circular_suffixes = [None] * len(text)
    for start_idx in range(len(text)):
        circular_suffixes[start_idx] = text[start_idx:len(text)] + text[0:start_idx]


    # sort based on the first character, second character, ....
    sorted_circular_suffixes = sorted(circular_suffixes)

    return "".join([x[-1] for x in sorted_circular_suffixes])

def get_order(char, i, order_table) -> int:
    """
    Given a character, it returns its order among the same characters in the first column (or last) in the sorted suffixes.
    Note that the order table isn't two-dimensional array but is one dimensional. In trade off, this function will traverse
    through each appearance of the same character until it finds the one looking for.

    :time complexity: O(X) where X represents the number of appearances of the same character in the suffixes.
    :aux space complexity: O(1)
    :param char: a character to find get order for
    :param i: the index of the character
    :param order_table: order table
    :return: the order of the given character
    """
    char_appearances = order_table[hash_char(char)]

    prev_appearances_count = 0
    for char_idx in char_appearances:
        if char_idx == i:
            return prev_appearances_count
        prev_appearances_count += 1

    raise ValueError("shouldn't come here")


def bwt_decode(text: str) -> str:
    """
    Implementation of BWT decoder. Use LF-mapping.

    Note: order table = nOccurences table in lecture note

    :time complexity: O(n) where n is the length of string
    :aux space complexity: O(n) for the encoded string, rank and order table
    :param text: encoded text (text to decode)
    :return: the original string
    """
    # create rank table and order table
    rank_table: list[Optional[int]] = [0]*(MAX_ASCII-MIN_ASCII+2)
    order_table: list[Optional[list[int]]] = [None]*(MAX_ASCII-MIN_ASCII+2)
    for i in range(len(text)):
        char = text[i]
        ascii_index = hash_char(char)

        if rank_table[ascii_index] == 0:
            order_table[ascii_index] = []

        rank_table[ascii_index] += 1
        order_table[ascii_index].append(i)

    # make the rank table cumulative
    acum = rank_table[0]
    rank_table[0] = 0
    for i in range(1, len(rank_table)):
        acum_temp = acum
        acum += rank_table[i]
        rank_table[i] = acum_temp

    # LF mapping
    decoded_text = []
    l_idx = 0
    for _ in range(len(text)):
        current_char = text[l_idx]

        decoded_text.append(current_char)
        l_idx = rank_table[hash_char(current_char)] + get_order(current_char, l_idx, order_table)

    decoded_text.pop()  # pop "$"
    decoded_text.reverse()

    return "".join(decoded_text)