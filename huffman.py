from __future__ import annotations
from typing import Optional

import heapq as hq
import bitarray

# later implement heap
MIN_ASCII, MAX_ASCII = 37, 126

class Node:
    def __init__(self, ascii=None) -> None:
        self.left = None
        self.right = None

        self.ascii = ascii

    def is_leaf(self):
        return bool(self.ascii)


class HeapElement:
    def __init__(self, freq: int, num_chars: int, asciies: list[int]):
        self.freq = freq
        self.num_chars = num_chars
        self.asciies = asciies  # a list of

    def __lt__(self, other: HeapElement):
        return (self.freq, self.height) < (other.freq, other.height)


def hash_ascii(char: str) -> int:
    assert MIN_ASCII <= ord(char) <= MAX_ASCII, "all characters must be in ascii value of 37-126"
    return ord(char)-MIN_ASCII

def huffman_encode(text: str) -> tuple:

    # create frequency table
    freq = [0]*(MAX_ASCII-MIN_ASCII+1)
    for char in text:
        freq[hash_ascii(char)] += 1

    # chars_for_heap = []
    # for i in range(len(freq)):
    #     if freq[i]:
    #         node = Node(freq[i], freq[i]+MIN_ASCII)
    #         node.character = i+37
    #         chars_for_heap.append(node)

    heap_elements = []
    for i in range(len(freq)):
        if freq[i]:
            heap_element = HeapElement(freq[i], 1, [i+MIN_ASCII])
            heap_elements.append(heap_element)

    # store the encoded bits at corresponding index
    code_table: list[Optional[bitarray.bitarray]] = [None]*(MAX_ASCII-MIN_ASCII+1)

    # heapify
    hq.heapify(heap_elements)

    # creating the code_table using heap
    while True:
        left = hq.heappop(heap_elements)
        right = hq.heappop(heap_elements)

        # "prepend" a bit to corresponding chars
        for ascii in left.asciies:
            if code_table[ascii-MIN_ASCII] is None:
                code_table[ascii - MIN_ASCII] = bitarray.bitarray()

            code_table[ascii-MIN_ASCII].append(0)

        for ascii in right.asciies:
            if code_table[ascii - MIN_ASCII] is None:
                code_table[ascii - MIN_ASCII] = bitarray.bitarray()

            code_table[ascii - MIN_ASCII].append(1)


        if len(heap_elements) == 0:
            break

        # insert the concatenated node
        concatenated = HeapElement(left.freq+right.freq, left.num_chars, right.num_chars, left.asciies.extend(right.asciies))  #TODO check the height equation
        hq.heappush(heap_elements, concatenated)

    # invert the bits
    for ascii_bits in code_table:
        if ascii_bits is not None:
            ascii_bits.invert()

    # traverse through the text to encode
    encoded_text = bitarray.bitarray()
    for char in text:
        encoded_text.extend(code_table[ord(char)-MIN_ASCII])

    return encoded_text, code_table

def huffman_decode(encoded_text: bitarray.bitarray, code_table: list) -> str:

    # create binary search tree to look up bits
    root = Node()

    for i in range(len(code_table)):
        code = code_table[i]
        if code is not None:
            # traverse through the tree until you find a new path -> brunch out -> reaches the end of the bits -> the character at the end
            current = root
            for i in range(len(code)):
                bit = code[i]

                # the leaf case
                if i == len(code)-1 and bit == 0:
                    current.left = Node(ascii=i+MIN_ASCII)
                    continue
                if i == len(code)-1 and bit == 1:
                    current.right = Node(ascii=i+MIN_ASCII)

                # normal cases
                if bit == 0 and current.left is not None:
                    current = current.left

                elif bit == 1 and current.left is not None:
                    current = current.right

                elif bit == 0 and current.left is None:
                    current.left = Node()
                    current = current.left

                elif bit == 1 and current.right is None:
                    current.right = Node()
                    current = current.right
                else:
                    raise ValueError("shouldn't come here")

    # actual decoding process
    decoded_chars = []
    i = 0
    while i < len(encoded_text):
        # traverse the BST while it reaches the leaf
        current = root
        while True:
            if current.is_leaf:
                decoded_chars.append(current.ascii)
            if encoded_text[i] == 0:
                current = current.left
            else:
                current = current.right

            i += 1

    return "".join(decoded_chars)

