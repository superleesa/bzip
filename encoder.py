import bitarray

from elias import elias_encode, decimal_to_bitarray
from bwt import bwt_encode_naive
from runlength_encoder import runlength_encoder

def pad_by_zeroes(encoded_text: bitarray.bitarray) -> bitarray.bitarray:
    # pad by 0s if there is remainder
    num_zeroes = 8 - len(encoded_text) % 8
    for _ in range(num_zeroes):
        encoded_text.append(0)

    return encoded_text


def encoder(text: str):
    # TODO consider edge cases such as when there is no text or one char
    encoded_length = elias_encode(len(text)+1)  # +1 for dollar symbol
    bwt_text = bwt_encode_naive(text)
    print("bwt_text")
    print(bwt_text)
    n_unique_chars, encoded_text, encoded_code_table = runlength_encoder(bwt_text)

    encoded_length.extend(n_unique_chars)
    encoded_length.extend(encoded_code_table)
    encoded_length.extend(encoded_text)

    encoded_text = pad_by_zeroes(encoded_length)

    return encoded_length


if __name__ == "__main__":
    text = "abcd"
    output = encoder(text)

    print(output)
    # outputting the content to the file
    with open("bwtencoded.bin", "wb") as file:
        file.write(output.tobytes())
