from utilities import MIN_ASCII, MAX_ASCII, hash_char, hash_back_tochar



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
