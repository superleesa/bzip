__author__ = "Satoshi Kashima"
__sid__ = 32678940
__description__ = "The implementation of run length decoder"

from typing import Optional

from utilities import MIN_ASCII, MAX_ASCII, hash_char, hash_back_tochar
from elias import elias_decode
from original_bitarray import BitArray


class BSTNode:
    """
    Represent the Binary Search Tree.
    Used in Huffman decoder.
    """
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


def runlength_decoder(encoded_text: BitArray, code_table: list, bwt_length: int) -> str:
    """
    Decode one run by one run by applying ELias decoding and huffman decoding.

    :param encoded_text: the encoded text in bitarray
    :param code_table: an array where each index represents the hashed character and its element represents the code word
    :param bwt_length: the length of the original bwt string
    :return: the decoded string
    """

    # create binary search tree for the codewords
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
    counter = 0

    while counter < bwt_length:
        # each run starts with how many times a char happens, and then actual code
        # do elias decoding
        n_appearances, encoded_text = elias_decode(encoded_text)


        # traverse the BST while it reaches the leaf
        # note: don't increment j after each outer loop because #edges = #nodes-1
        current = root
        j = 0
        while True:
            if current.is_leaf():
                decoded_chars.append(current.char*n_appearances)
                break

            if encoded_text[j] == 0:
                current = current.left
            else:
                current = current.right

            j += 1

        counter += n_appearances
        encoded_text = encoded_text[j:]


    return "".join(decoded_chars)
