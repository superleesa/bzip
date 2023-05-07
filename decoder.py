from typing import Optional
from bitarray import bitarray

from elias import elias_encode, decimal_to_bitarray, bitarray_to_decimal
from bwt import bwt_decode
from runlength_decoder import runlength_decoder
from elias import elias_decode
from utilities import MAX_ASCII, MIN_ASCII, hash_char, hash_char_from_ascii


def split_table_and_body(data_bits: bitarray, n_unique_chars: int) -> tuple[bitarray, list]:
    code_table: list[Optional[bitarray]] = [None] * (MAX_ASCII - MIN_ASCII + 2)

    for _ in range(n_unique_chars):
        char_idx = hash_char_from_ascii(bitarray_to_decimal(data_bits[:7]))
        codeword_length, remainder = elias_decode(data_bits[7:])
        code_table[char_idx] = remainder[:codeword_length]  # note: this is constant operation (see implementation)

        data_bits = remainder[codeword_length:]

    body = data_bits

    return body, code_table


def decoder(encoded_text: bitarray) -> str:
    """
    encoding format:
    bwt_length (elias),
    n_unique_key (elias),
    table (ascii, elias run length, huffman codeword),
    main_text (elias length, huffman codeword)

    :param encoded_text:
    :return:
    """
    # separate the header and the body part
    bwt_length, remainder = elias_decode(encoded_text)
    n_unique_chars, remainder = elias_decode(remainder)
    print("bwt_length")
    print(bwt_length)
    print("n_unique_characters")
    print(n_unique_chars)
    print(remainder)

    body, code_table = split_table_and_body(remainder, n_unique_chars)

    print(body)
    decoded_text = runlength_decoder(body, code_table, bwt_length)

    # TODO: note there can be 0 paddings at the end -> handle them

    # TODO apply bwt_decoder
    original_text = bwt_decode(decoded_text)

    return original_text

if __name__ == "__main__":
    # TODO later get input from the cmd
    filename = "bwtencoded.bin"
    ba = bitarray()
    with open(filename, "rb") as file:
        ba.fromfile(file)
        print(ba)

        print(decoder(ba))
