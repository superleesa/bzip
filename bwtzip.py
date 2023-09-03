__author__ = "Satoshi Kashima"
__sid__ = 32678940

import sys

from elias import elias_encode
from bwt import bwt_encode_naive, bwt_encode_with_ukkonen
from runlength_encoder import runlength_encoder
from original_bitarray import BitArray

def pad_by_zeroes(encoded_text: BitArray) -> BitArray:
    # pad by 0s if there is remainder
    num_zeroes = 8 - len(encoded_text) % 8
    for _ in range(num_zeroes):
        encoded_text.append(0)

    return encoded_text


def encoder(text: str) -> BitArray:
    """
    encoding format:
    bwt_length (elias),
    n_unique_key (elias),
    table (ascii, elias run length, huffman codeword),
    main_text (elias length, huffman codeword)
    """
    encoded_length = elias_encode(len(text)+1)  # +1 for dollar symbol
    bwt_text = bwt_encode_with_ukkonen(text)  # change to bwt_encode_naive(text) see the difference
    # print("bwt_text")
    # print(bwt_text)
    n_unique_chars, encoded_text, encoded_code_table = runlength_encoder(bwt_text)

    encoded_length.extend(n_unique_chars)
    encoded_length.extend(encoded_code_table)
    encoded_length.extend(encoded_text)

    encoded_text = pad_by_zeroes(encoded_length)

    return encoded_text


if __name__ == "__main__":
    _, text_filename = sys.argv

    with open(text_filename, "r") as file:
        text = file.readline()

    encoded_text = encoder(text)
    output_filename = "bwtencoded.bin"

    with open(output_filename, "wb") as file:
        file.write(encoded_text.tobytes())
