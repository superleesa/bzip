from typing import Optional

MIN_ASCII, MAX_ASCII = 37, 126

def hash_ascii(char: str) -> int:
    assert MIN_ASCII <= ord(char) <= MAX_ASCII, "all characters must be in ascii value of 37-126"
    return ord(char)-MIN_ASCII

def bwt_encode(text: str) -> str:
    # use Ukkonen to generate the encoded text
    pass

def get_order(char, i, order_table) -> int:
    char_appearances = order_table[hash_ascii(char)]

    prev_appearances_count = 0
    for char_idx in char_appearances:
        if char_idx == i:
            return prev_appearances_count
        prev_appearances_count += 1


def bwt_decode(text: str) -> str:
    # create rank table and order table
    rank_table: list[Optional[int]] = [None]*(MAX_ASCII-MIN_ASCII+1)
    order_table: list[Optional[list[int]]] = [None]*(MAX_ASCII-MIN_ASCII+1)
    for i in range(len(text)):
        char = text[i]
        ascii_index = hash_ascii(char)

        if rank_table[ascii_index] is None:
            rank_table[ascii_index] = 0
            order_table[ascii_index] = []

        rank_table[ascii_index] += 1
        order_table[ascii_index].append(i)

    # make the rank table cumulative
    for i in range(1, len(rank_table)):
        rank_table[i] = rank_table[i-1] + rank_table[i]

    # LF mapping
    decoded_text = []
    l_idx = 0
    for _ in range(len(text)):
        current_char = text[l_idx]
        decoded_text.append(current_char)
        l_idx = rank_table[hash_ascii(current_char)] + get_order(current_char, l_idx, order_table)

    decoded_text.reverse()

    return ".".join(decoded_text)
