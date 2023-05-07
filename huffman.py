from __future__ import annotations
from typing import Optional

import heapq as hq
import bitarray

# later implement heap
MIN_ASCII, MAX_ASCII = 37, 126

class BSTNode:
    def __init__(self, char: Optional[str] = None) -> None:
        self.left: Optional[BSTNode] = None
        self.right: Optional[BSTNode] = None
        self.bit = None

        assert char != "", "char shouldn't be empty"
        self.char: Optional[str] = char

    def is_leaf(self) -> bool:
        return self.char is not None

    def __str__(self):
        if self.is_leaf():
            return str((self.bit, self.char))
        else:
            return str(self.bit)

# def show_all_bst_elements(current: BSTNode):
#
#     if current.left is not None:
#         left = show_all_bst_elements(current.left)
#     if current.right is not None:
#         right = show_all_bst_elements(current.right)
#
#     if left and right:
#         return
#
#
#     result = [show_all_bst_elements(current.left), show_all_bst_elements(current.right)]
#
#
#     return result

class HeapElement:
    def __init__(self, freq: int, num_chars: int, chars_asciis: list[int]) -> None:
        self.freq: int = freq
        self.num_chars: int = num_chars
        self.chars_asciis: list[int] = chars_asciis  # a list of characters in ascii

    def __lt__(self, other: HeapElement) -> bool:
        return (self.freq, self.num_chars) < (other.freq, other.num_chars)

    def __str__(self) -> str:
        return str((self.freq, self.num_chars, self.chars_asciis))


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

def huffman_encode(text: str) -> tuple:

    # create frequency table
    freq = [0]*(MAX_ASCII-MIN_ASCII+2)
    for char in text:
        freq[hash_char(char)] += 1


    heap_elements = []
    for i in range(len(freq)):
        if freq[i]:
            heap_element = HeapElement(freq[i], 1, [i])
            heap_elements.append(heap_element)

    # store the encoded bits at corresponding index
    code_table: list[Optional[bitarray.bitarray]] = [None]*(MAX_ASCII-MIN_ASCII+2)

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

    # traverse through the text to encode
    encoded_text = bitarray.bitarray()
    for char in text:
        encoded_text.extend(code_table[hash_char(char)])


    return encoded_text, code_table

def huffman_decode(encoded_text: bitarray.bitarray, code_table: list) -> str:
    """

    :param encoded_text:
    :param code_table: an array where each index represents the hashed character and its element represents the code word
    :return:
    """

    # create binary search tree to look up bits
    root = BSTNode()

    for i in range(len(code_table)):

        code = code_table[i]
        if code is not None:
            # insert each character (represented in bits) into the bst
            current = root
            for j in range(len(code)):
                bit = code[j]

                # the leaf case
                if j == len(code)-1 and bit == 0:
                    current.left = BSTNode(hash_back_tochar(i))
                    continue
                if j == len(code)-1 and bit == 1:
                    current.right = BSTNode(hash_back_tochar(i))
                    continue

                # normal cases
                if bit == 0 and current.left is not None:
                    current = current.left

                elif bit == 1 and current.right is not None:
                    current = current.right

                elif bit == 0 and current.left is None:
                    current.left = BSTNode()
                    current = current.left

                elif bit == 1 and current.right is None:
                    current.right = BSTNode()
                    current = current.right
                else:
                    raise ValueError("shouldn't come here")

    # actual decoding process
    decoded_chars = []
    j = 0
    while j < len(encoded_text):
        # traverse the BST while it reaches the leaf
        # note: don't increment j after each outer loop because #edges = #nodes-1
        current = root
        while True:
            if current.is_leaf():
                decoded_chars.append(current.char)
                break
            if encoded_text[j] == 0:
                current = current.left
            else:
                current = current.right

            j += 1



    return "".join(decoded_chars)

