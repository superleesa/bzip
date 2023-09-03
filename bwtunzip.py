__author__ = "Satoshi Kashima"
__sid__ = 32678940

from typing import Optional
import sys

from bwt import bwt_decode
from runlength_decoder import runlength_decoder
from elias import elias_decode
from utilities import MAX_ASCII, MIN_ASCII, hash_char_from_ascii
from original_bitarray import BitArray


def bytes_to_bitarray(byte_data) -> BitArray:
    num = int.from_bytes(byte_data, byteorder='big')  # convert bytes into integer
    n_bits = len(byte_data) * 8  # calculate the length

    # edge case (if no text is encoded)
    if num == 0:
        return BitArray()

    # create a BitArray instance with the integer and number of bits
    return BitArray(num, n_bits=n_bits)

def split_table_and_body(data_bits: BitArray, n_unique_chars: int) -> tuple[BitArray, list]:
    code_table: list[Optional[BitArray]] = [None] * (MAX_ASCII - MIN_ASCII + 2)

    for _ in range(n_unique_chars):
        char_idx = hash_char_from_ascii(data_bits[:7].to_decimal())
        codeword_length, remainder = elias_decode(data_bits[7:])
        code_table[char_idx] = remainder[:codeword_length]  # note: this is constant operation (see implementation)

        data_bits = remainder[codeword_length:]

    body = data_bits

    return body, code_table


def decoder(encoded_text: BitArray) -> str:
    """
    encoding format:
    bwt_length (elias),
    n_unique_key (elias),
    table (ascii, elias run length, huffman codeword),
    main_text (elias length, huffman codeword)
    """
    # separate the header and the body part
    bwt_length, remainder = elias_decode(encoded_text)  # decoding bwt_length
    n_unique_chars, remainder = elias_decode(remainder)  # decoding  n_unique_chars

    body, code_table = split_table_and_body(remainder, n_unique_chars)  # split the header and the body
    decoded_text = runlength_decoder(body, code_table, bwt_length)  # runlength decoding
    original_text = bwt_decode(decoded_text)  # bwt decoding

    return original_text


if __name__ == "__main__":
    _, encoded_text_filename = sys.argv

    with open(encoded_text_filename, "rb") as file:
        ba = bytes_to_bitarray(file.read())

    output_filename = "recovered.txt"
    with open(output_filename, "w") as file:
        file.write(decoder(ba))

