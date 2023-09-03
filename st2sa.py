__author__ = "Satoshi Kashima"
__sid__ = 32678940

import sys

from ukkonen import ukkonen, Node


def inorder_traversal(current: Node) -> list[int]:
    """
    Traverses through the given node inorder
    """
    result = []

    if current.is_leaf:
        result.append(current.suffix_starting_idx+1)
        return result  # +1 for 1-base indexing

    for node in current.edges:
        if node is not None:
            result.extend(inorder_traversal(node))

    return result

def suffix_array(text: str) -> list[int]:
    """
    1) appends "$" symbol
    2) invokes Ukkonen
    3) apply inorder traversal to the created tree to obtain indexes corresponding to the suffix array
    """
    result = [None]*(len(text)+1)
    text += "$"  # O(n)
    root = ukkonen(text)
    suffix_array_idxs = inorder_traversal(root)

    return suffix_array_idxs


def format_output(result):
    oup_elements = []
    for match in result:
        oup_elements.append(str(match) + "\n")

    return "".join(oup_elements)


if __name__ == "__main__":
    # note: the output is 1-based index
    _, filename = sys.argv

    with open(filename, "r") as file:
        text = file.readline()

    suffix_array_indices = suffix_array(text)

    output_filename = "output_sa.txt"
    with open(output_filename, "w") as file:
        file.write(format_output(suffix_array_indices))


