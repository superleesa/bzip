from optimized_ukkonen import ukkonen_v2, Node, MIN_ASCII, MAX_ASCII
# from elias import elias_encode, elias_decode, decimal_to_bitarray
#
# encoded = elias_encode(561)
# print(encoded)
# # print(decimal_to_bitarray(112))
#
# print(elias_decode(encoded))


# for visualization purposes
def getinfo_tree(root):
    return getinfo_tree_aux(root)


def getinfo_tree_aux(node):

    result = [(node.start, str(node.end)), {}]

    for idx, connected_node in enumerate(node.edges):
        if isinstance(connected_node, Node):
            result[1][chr(idx+MIN_ASCII)] = getinfo_tree_aux(connected_node)

    return result


def visualize_tree(collected_data):
    pass


if __name__ == "__main__":
    root = ukkonen_v2("abcabx")
    print(getinfo_tree(root))

# case 1: there is no start/end
# if current_node.start == current_node.end and i-k+1 > 1:
#     previous_node.start = k+1
#     previous_node.end = i
#     break