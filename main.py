from optimized_ukkonen import ukkonen_v2, MIN_ASCII, MAX_ASCII
from optimized_ukkonen_v4 import ukkonen_v3, Node
from huffman import huffman_encode, huffman_decode, hash_back_tochar
from utilities import generate_random_string
from runlength_encoder import runlength_encoder
from runlength_decoder import runlength_decoder
from encoder import encoder
from decoder import decoder

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
    unsuccessful_cases = []
    for _ in range(100000):
        expected = generate_random_string()
        bitstream = encoder(expected)
        actual = decoder(bitstream)

        if actual != expected:
            unsuccessful_cases.append((actual, expected))

    print(unsuccessful_cases)
    # text = ")4JBI/7<mv_|B7K"
    # bitarr = encoder(text)
    # print(bitarr)
    # print(decoder(bitarr))
    # # text = "eheelloiamesatoshie"

    # print(text == huffman_decode(*huffman_encode(text)))

