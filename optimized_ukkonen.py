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
        self.is_leaf = True  # set to false when brunching out

        # for suffix link
        self.suffix_link: Optional[Node] = None


class GlobalEnd:
    def __init__(self, i):
        self.i = i

    def increment(self):
        self.i += 1

    def __str__(self):
        return str(self.i)


def compare_edge(k: int, current_node: Node, i: int, global_end: GlobalEnd, text: str) -> tuple[Optional[int], bool]:
    reached_case3 = False
    end: int = current_node.end.i if isinstance(current_node.end, GlobalEnd) else current_node.end

    # case3: occurs when the substring inserting has length = 1 and there is an existing edge for it (from the root)
    if k > i:
        reached_case3 = True
        return None, reached_case3

    for existing_idx in range(current_node.start, end + 1):

        # case 2 - branch out
        if text[existing_idx] != text[k]:
            # create two new nodes: the existing and the one inserting
            # put them in node.link of the current node-> you hash first to find where to put
            existing_branch = Node(start=existing_idx + 1, end=global_end)
            current_node.end = existing_idx - 1
            current_node.is_leaf = False
            inserting_branch = Node(start=k + 1, end=global_end)
            current_node.edges[hash_ascii(text[existing_idx])] = existing_branch
            current_node.edges[hash_ascii(text[k])] = inserting_branch
            reached_case3 = True
            return None, reached_case3

        # case 3 - the one already exists longer: stop
        if k == i:
            reached_case3 = True
            return None, reached_case3

        k += 1

    return k, reached_case3

def do_extension(j: int, i: int, global_end: GlobalEnd, root: Node, text: str) -> Optional[int]:
    # iterates through the nodes to find where the current substring should go
    current_node = root
    k = j  # pointer to the index being compared of a current substring text[j:i+1]
    reached_case3 = False
    while True:
        # print("comes here")
        previous_node = current_node
        current_node = previous_node.edges[hash_ascii(text[k])]

        # case 2-alt: branch at the root; or, brunch at an internal node
        if current_node is None and previous_node.is_root or current_node is None and not previous_node.is_leaf:
            previous_node.edges[hash_ascii(text[k])] = Node(start=k+1, end=global_end)
            break

        # case 1: extension if there aren't other edges at a node
        # occurs at middle (after at least 1 edge=branch=iteration)
        if current_node is None and not previous_node.is_root and previous_node.is_leaf:
            previous_node.start = k_prev_start
            previous_node.end = global_end
            break

        # actual comparison
        k_end, reached_case3 = compare_edge(k+1, current_node, i, global_end, text)

        # reached the end already during the actual comparison(case2 or case3)
        if k_end is None:
            break

        k_prev_start = k+1
        k = k_end+1

    j_next = j if reached_case3 else None

    return j_next



def ukkonen_v2(text: str) -> Node:
    # create implicit tree

    root = Node(is_root=True)
    global_end = GlobalEnd(-1)
    j_next: Optional[int] = None  # used for showstopper; if this value is set an integer,this values represents the j to start the extension from

    for i in range(len(text)):
        global_end.increment()

        start = j_next if j_next is not None else i

        for j in range(start, i+1):
            j_next = do_extension(j, i, global_end, root, text)

            # reached case 3 during comparison
            if j_next is not None:
                break

    return root