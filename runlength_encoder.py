from __future__ import annotations
from typing import Optional
from math import log10, ceil

import heapq as hq
import bitarray

from elias import elias_encode, decimal_to_bitarray
from utilities import MIN_ASCII, MAX_ASCII, hash_char, hash_back_tochar


class HeapElement:
    def __init__(self, freq: int, num_chars: int, chars_asciis: list[int]) -> None:
        self.freq: int = freq
        self.num_chars: int = num_chars
        self.chars_asciis: list[int] = chars_asciis  # a list of characters in ascii

    def __lt__(self, other: HeapElement) -> bool:
        return (self.freq, self.num_chars) < (other.freq, other.num_chars)

    def __str__(self) -> str:
        return str((self.freq, self.num_chars, self.chars_asciis))


def runlength_encoder(text: str) -> tuple[bitarray.bitarray, bitarray.bitarray, bitarray.bitarray]:
    """

    :param text: an encoded text using BWT
    :return: bitarray
    """


    # MAIN PART
    # create frequency table
    freq = [0] * (MAX_ASCII - MIN_ASCII + 2)
    for char in text:
        freq[hash_char(char)] += 1

    num_unique_chars = 0
    heap_elements = []
    for i in range(len(freq)):
        if freq[i]:
            heap_element = HeapElement(freq[i], 1, [i])
            heap_elements.append(heap_element)
            num_unique_chars += 1

    encoded_num_unique_chars = elias_encode(num_unique_chars)

    # store the encoded bits at corresponding index
    code_table: list[Optional[bitarray.bitarray]] = [None] * (MAX_ASCII - MIN_ASCII + 2)

    # heapify
    hq.heapify(heap_elements)

    # creating the code_table using heap
    while True:
        left: HeapElement = hq.heappop(heap_elements)
        right: HeapElement = hq.heappop(heap_elements)

        # "prepend" a bit to corresponding chars
        for char_idx in left.chars_asciis:
            if code_table[char_idx] is None:
                code_table[char_idx] = bitarray.bitarray()

            code_table[char_idx].append(0)

        for char_idx in right.chars_asciis:
            if code_table[char_idx] is None:
                code_table[char_idx] = bitarray.bitarray()

            code_table[char_idx].append(1)

        if len(heap_elements) == 0:
            break

        assert left.chars_asciis is not None and right.chars_asciis is not None, "should not be none"

        # mutate the left node and pass it again as the parent node of the right and left node
        left.freq += right.freq
        left.num_chars += right.num_chars
        left.chars_asciis.extend(right.chars_asciis)

        # insert the concatenated node
        hq.heappush(heap_elements, left)

    # reverse the bits
    for ascii_bits in code_table:
        if ascii_bits is not None:
            ascii_bits.reverse()

    # traverse through the text to do run length encoding
    # for each consecutive same chars, combine them all together e.g. aaaa -> 4a
    # elias + huffman
    encoded_text = bitarray.bitarray()
    accum = 1
    prev_char = text[0]
    for i in range(1, len(text)):
        char = text[i]
        if char == prev_char:
            accum += 1
        else:
            run_length = elias_encode(accum)
            encoded_text.extend(run_length)
            encoded_text.extend(code_table[hash_char(prev_char)])

            accum = 1
            prev_char = char

    # for the remaining char (can be 1 or many)
    run_length = elias_encode(accum)
    encoded_text.extend(run_length)
    encoded_text.extend(code_table[hash_char(prev_char)])

    # encode table
    encoded_code_table = bitarray.bitarray()
    for char_idx, code_word in enumerate(code_table):
        if code_word is not None:
            char_ascii = create_fixed_length_ascii_bitarray(hash_back_tochar(char_idx))  # TODO: the ascii must be in 7 bits
            char_length = elias_encode(len(code_word))

            encoded_code_table.extend(char_ascii)
            encoded_code_table.extend(char_length)
            encoded_code_table.extend(code_word)

    return encoded_num_unique_chars, encoded_text, encoded_code_table


def create_fixed_length_ascii_bitarray(char: str):
    # TODO change this later on
    assert len(char) == 1, "length of the string must be 1"

    ascii_value = ord(char)  # get the ASCII value of the character
    binary_string = bin(ascii_value)[2:].zfill(7)  # convert to binary string and pad with zeros to 7 bits
    return bitarray.bitarray(binary_string)


# ascii_val = ord(char)
#     ascii_val_legnth = ceil(log10(ascii_val))
#     n_paddings = 7 - ascii_val_legnth
#     ascii_bitarray = bitarray.bitarray("0"*n_paddings)
#     ascii_bitarray.extend(bitarray.bitarray(ascii_val))








