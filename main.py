from optimized_ukkonen import ukkonen_v2, MIN_ASCII, MAX_ASCII
from optimized_ukkonen_v4 import ukkonen_v3, Node
from huffman import huffman_encode, huffman_decode, hash_back_tochar

from pprint import pprint

# from elias import elias_encode, elias_decode, decimal_to_bitarray
#
# encoded = elias_encode(561)
# print(encoded)
# # print(decimal_to_bitarray(112))
#
# print(elias_decode(encoded))



# # text = "abab": this exmples does not require suffix link active node
#     # text = "abcabxabcyab" # creates one suffix link and uses it
#     text = "mississippissipg$"  # this example requires suffix link
#     # text = "missippimippimmisi$"
#     root = ukkonen_v3(text)
#
#     # pprint(getinfo_tree(root))
#
#     # pprint(getinfo_tree_aux_v2(root, text))


if __name__ == "__main__":
    text = "eheelloiamesatoshie"

    print(text == huffman_decode(*huffman_encode(text)))

