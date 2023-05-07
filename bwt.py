from typing import Optional

MIN_ASCII, MAX_ASCII = 37, 126

def hash_ascii(char: str) -> int:
    assert MIN_ASCII <= ord(char) <= MAX_ASCII or char == "$", "all characters must be in ascii value of 37-126, or $"

    if char == "$":
        return 0
    else:
        # +1 to accommodate for "$"
        return ord(char)-MIN_ASCII+1

def bwt_encode(text: str) -> str:
    # use Ukkonen to generate the encoded text
    pass

def bwt_encode_naive(text: str):

    # create circular suffixes
    text = text + "$"
    circular_suffixes = [None] * len(text)
    for start_idx in range(len(text)):
        circular_suffixes[start_idx] = text[start_idx:len(text)] + text[0:start_idx]


    # sort based on the first character
    sorted_circular_suffixes = sorted(circular_suffixes)

    return "".join([x[-1] for x in sorted_circular_suffixes])

def get_order(char, i, order_table) -> int:
    char_appearances = order_table[hash_ascii(char)]

    prev_appearances_count = 0
    for char_idx in char_appearances:
        if char_idx == i:
            return prev_appearances_count
        prev_appearances_count += 1

    raise ValueError("shouldn't come here")


def bwt_decode(text: str) -> str:
    """

    :param text: encoded text (text to decode)
    :return:
    """
    # create rank table and order table
    rank_table: list[Optional[int]] = [0]*(MAX_ASCII-MIN_ASCII+2)
    order_table: list[Optional[list[int]]] = [None]*(MAX_ASCII-MIN_ASCII+2)
    for i in range(len(text)):
        char = text[i]
        ascii_index = hash_ascii(char)

        if rank_table[ascii_index] == 0:
            order_table[ascii_index] = []

        rank_table[ascii_index] += 1
        order_table[ascii_index].append(i)

    # make the rank table cumulative
    print(rank_table)
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
        l_idx = rank_table[hash_ascii(current_char)] + get_order(current_char, l_idx, order_table)

    decoded_text.pop()  # pop "$"
    decoded_text.reverse()

    return "".join(decoded_text)

if __name__ == "__main__":
    text = "isisisis"
    encoded = bwt_encode_naive(text)
    print(encoded)

    decoded = bwt_decode(encoded)
    print(decoded)