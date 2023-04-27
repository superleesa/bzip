from typing import Optional


MIN_ASCII, MAX_ASCII = 37, 126

def hash_ascii(char: str) -> int:
    assert MIN_ASCII <= ord(char) <= MAX_ASCII, "all characters must be in ascii value of 37-126"
    return ord(char)-MIN_ASCII

class Node:
    def __init__(self, start=None, end=None, is_root=False):
        self.edges: list[Optional[Node]] = [None] * (MAX_ASCII - MIN_ASCII + 1)
        self.start: Optional[int] = start
        self.end: Optional[int] = end  # inclusive
        self.is_root = is_root

        # for suffix link
        self.suffix_link: Optional[Node] = None


class GlobalEnd:
    def __init__(self, i):
        self.i = i

    def increment(self):
        self.i += 1


def naive_ukkonen(text: str):
    # create implicit tree

    root = Node(is_root=True)
    global_end = GlobalEnd(0)

    for i in range(len(text)):
        global_end.increment()

        start = prev_j if is_case_three else i
        for j in range(start, i+1):

            # iterates through the nodes to find where the current substring should go
            current_node = root
            k = j  # pointer to the index being compared of a current substing text[j:i+1]
            while True:
                # print("comes here")
                previous_node = current_node
                current_node = previous_node.edges[hash_ascii(text[k])]

                # case 2-alt: branches at the root
                if current_node is None and previous_node.is_root:
                    previous_node.edges[hash_ascii(text[j])] = Node(start=j + 1, end=global_end)
                    break

                # case 1, or case 2-alt: extension if there aren't other edges; brunch out if there is another edge
                # occurs at middle (after at least 1 edge=branch=iteration)
                if current_node is None and not previous_node.is_root:
                    previous_node.start = starting_k
                    previous_node.end = global_end
                    break

                reaches_end = False
                starting_k = k+1
                is_case_three = False
                end = current_node.i if isinstance(current_node, GlobalEnd) else current_node.end

                for l in range(current_node.start, end+1):
                    # case 2 - branch out
                    if text[l] != text[k]:


                        # create two new nodes: the existing and the one inserting
                        # put them in node.link of the current node-> you hash first to find where to put
                        existing_branch = Node(start=l+1, end=current_node.end)
                        current_node.end = l - 1
                        inserting_branch = Node(start=k+1, end=global_end)
                        current_node.edges[hash_ascii(text[l])] = existing_branch
                        current_node.edges[hash_ascii(text[k])] = inserting_branch
                        reaches_end = True
                        break

                    # case 3 - the one already exists longer: stop
                    if k == i:
                        reaches_end = True
                        is_case_three = True
                        break

                    k += 1  # update k

                if reaches_end:
                    break

            if is_case_three:
                prev_j = j
                break


    return root


# for visualization purposes
def getinfo_tree(root: Node):
    return getinfo_tree_aux(root)


def getinfo_tree_aux(node):

    result = [(node.start, node.end), {}]

    for idx, connected_node in enumerate(node.edges):
        if isinstance(connected_node, Node):
            result[1][chr(idx+MIN_ASCII)] = getinfo_tree_aux(connected_node)

    return result


def visualize_tree(collected_data):
    pass


if __name__ == "__main__":
    root = naive_ukkonen("aaaa")
    print(getinfo_tree(root))

# case 1: there is no start/end
# if current_node.start == current_node.end and i-k+1 > 1:
#     previous_node.start = k+1
#     previous_node.end = i
#     break