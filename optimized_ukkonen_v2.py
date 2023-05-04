from __future__ import annotations
from typing import Optional

# Ukkonen Version 3 - with trick1, 2, 4, and suffix link (without skip count)

MIN_ASCII, MAX_ASCII = 37, 126

def hash_ascii(char: str) -> int:
    assert MIN_ASCII <= ord(char) <= MAX_ASCII, "all characters must be in ascii value of 37-126"
    return ord(char)-MIN_ASCII




class ActivePointer:
    """
    if self.node = root, ignore edge and length and start the comparison from j

    Can be used in two ways:
    1) to move from one extension to another quickly using suffix link; active node points to the last internal node visited in a traversal
    2) for showstopper; active node points to the last character visited in the previous iteration
    """
    def __init__(self):
        self.node: Optional[Node] = None
        self.edge_idx: Optional[int] = None
        self.length: Optional[int] = None  # does not include embded one

        # starting j of the edge (does not include the embed one; it's the second one)
        self.j_start: Optional[int] = None

    def update_node(self, node: Node):
        self.node = node

    def set_length(self, length: int):
        self.length = length  # includes the start and end (BUT: does not include the letter embedded in the previous node)

    def set_edge_idx(self, edge_idx: int):
        self.edge_idx = edge_idx





class SuffixLinkActivePointer(ActivePointer):
    def __init__(self, node: Optional[Node] = None, showstopper_activenode: ShowstopperActivePointer = None):
        super().__init__()

        if showstopper_activenode and node:
            raise ValueError("only one of showstopper and node should be used to instantiate suffixlink activenode")

        if showstopper_activenode is not None:
            self.convert_from_showstopper_activenode(showstopper_activenode)

        if node is not None:
            self.node = node
            self.length = 0



    def convert_from_showstopper_activenode(self, showstopper_activenode: ShowstopperActivePointer):
        self.node = showstopper_activenode.node
        self.edge_idx = showstopper_activenode.edge_idx
        self.length = showstopper_activenode.length

    def add_jstart(self, j_start: int):
        self.j_start = j_start


    def get_starting_k(self):
        # use this method for suffix link
        # includes the index of the embded char
        return self.j_start-1



class Node:
    """
    The first character of each edge is embedded in previous node to enable accessing into edges in a constant time.
    """
    def __init__(self, start=None, end=None, is_root=False):
        self.start: Optional[int] = start  # the index of a second character on an edge
        self.end: Optional[int] = end  # the index of the last character (inclusive)

        # outward edges from this node
        # each index represents the starting character of an outward edge
        self.edges: list[Optional[Node]] = [None] * (MAX_ASCII - MIN_ASCII + 1)

        self.is_root = is_root

        # used to distinguish case1 vs. case2-alt
        self.is_leaf = True  # set to false when brunching out

        # for suffix link
        self.suffix_link: Optional[Node] = None

    def connect_edge(self, first_char: str, node: Node) -> None:
        self.edges[hash_ascii(first_char)] = node

    def get_edge_starting_with_char(self, char: str) -> Optional[Node]:
        return self.edges[hash_ascii(char)]



class GlobalEnd:
    def __init__(self, i):
        self.i = i

    def increment(self):
        self.i += 1

    def __str__(self):
        return str(self.i)


def branch_out(k: int, existing_idx: int, current_node: Node, active_node: ActivePointer, previous_branched_node: Node,
               root: Node, global_end: GlobalEnd, text: str):
    """
    Makes extension to the current node and resolves pending suffix link from the previous extension
    Modifies the attributes of current node and active node

    :param k:
    :param existing_idx:
    :param current_node:
    :param active_node:
    :param root:
    :param previous_branched_node:
    :param global_end:
    :param text:
    :return:
    """

    # create two new nodes: the existing and the one inserting
    # put them in node.link of the current node-> you hash first to find where to put
    existing_branch = Node(start=existing_idx + 1, end=global_end)
    current_node.end = existing_idx - 1
    current_node.is_leaf = False
    inserting_branch = Node(start=k + 1, end=global_end)
    current_node.connect_edge(text[existing_idx], existing_branch)
    current_node.connect_edge(text[k], inserting_branch)

    # active node related procedure
    # even if this function is used during showstopper it works
    # because this function will only be used when there is a branch.
    # if there is a branch, the showstopper will stop and normal extensions uses suffixlink activenode
    active_node.set_length(current_node.end - current_node.start + 1)

    # suffix link related procedures
    current_node.suffix_link = root  # connect the branched node to root temporarily
    # RESOLVE: connect the previously branched node in a previous extension to the branched node
    if previous_branched_node is not None:
        previous_branched_node.suffix_link = current_node
    previous_branched_node = current_node

    return previous_branched_node


def compare_edge(k: int, current_node: Node, i: int, global_end: GlobalEnd,
                 active_node: ActivePointer, root: Node, previous_branched_node: Optional[Node], text: str)\
        -> tuple[Optional[int], bool, Optional[Node]]:
    """
    Handles the actual comparison of characters (on an edge) between the ones that exist in the tree and the one inserting right now
    Note: changes attributes of active_node inside
    :param active_node:
    :param previous_branched_node:
    :param root:
    :param k:
    :param current_node:
    :param i:
    :param global_end:
    :param text:
    :return:
    """

    reached_case3: bool = False
    end: int = current_node.end.i if isinstance(current_node.end, GlobalEnd) else current_node.end

    # case3: occurs when the substring inserting has length = 1 and there is an existing edge for it (from the root)
    if k+1 > i:
        reached_case3 = True
        return None, reached_case3, previous_branched_node

    for existing_idx in range(current_node.start, end + 1):
        k += 1

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

            # active node related procedure
            active_node.set_length(current_node.end - current_node.start + 1)

            # suffix link related procedures
            current_node.suffix_link = root  # connect the branched node to root temporarily
            if previous_branched_node is not None:
                previous_branched_node.suffix_link = current_node  # connect the previously branched node in a previous extension to the branched node
            previous_branched_node = current_node

            # TODO need to return active node too
            return None, reached_case3, previous_branched_node

        # case 3 - the one already exists longer: stop
        if k == i:
            reached_case3 = True
            return None, reached_case3, previous_branched_node

    return k, reached_case3, previous_branched_node

def do_extension(j: int, i: int, global_end: GlobalEnd, active_node: ActivePointer, root: Node, previous_branched_node: Optional[Node], text: str) -> tuple[Optional[int], Node]:
    """
    Iterates through the nodes to find where the current substring should go
    changes attributes of active node inside
    :param previous_branched_node:
    :param j:
    :param i:
    :param global_end:
    :param root:
    :param previous_branch_node:
    :param text:
    :return:
    :effect: changes the tree (adds a node, modifies node.start, node.end)
    """

    current_node: Optional[Node] = root
    k: int = j  # pointer to the index being compared of a current substring text[j:i+1]
    reached_case3: bool = False
    edge_defined = False

    # TODO check using suffix link

    # check active node
    if active_node.node.suffix_link != root:
        # suffix link points to a node that is not node -> does not need to traverse naively
        k = active_node.j_start-1  # -1 because j_start does not include the embed one
        current_node = active_node.node.suffix_link
        edge_defined = True
        # TODO get length too for skip count


    # if active node is root (or the suffix link of the active node points to the root), need to traverse naively

    while True:
        # TODO check this part
        previous_node: Node = current_node  # the previous node the current substring visited
        # if we have an effective active node, it stores edge idx already
        edge_idx = active_node.edge_idx if edge_defined else hash_ascii(text[k])
        edge_defined = False
        current_node = previous_node.edges[edge_idx]

        # case 2-alt: branch at the root; or, brunch at an internal node
        if current_node is None and previous_node.is_root or current_node is None and not previous_node.is_leaf:
            # active node update: +2 because: 1) both start and end are inclusive
            active_node.set_length(previous_node.end-previous_node.start+1)
            previous_node.connect_edge(text[k], Node(start=k+1, end=global_end))
            break

        # case 1: extension if there aren't other edges at a node
        if current_node is None and not previous_node.is_root and previous_node.is_leaf:
            active_node.set_length(previous_node.end-previous_node.start+1)  # active node length update
            previous_node.start = k_prev_start
            previous_node.end = global_end
            break

        # TODO - update active node
        active_node.update_node(previous_node)
        active_node.set_edge_idx(hash_ascii(text[k]))

        # actual comparison
        k_end, reached_case3, previous_branched_node = \
            compare_edge(k, current_node, i, global_end, active_node, root, previous_branched_node, text)

        # reached the end already during the actual comparison(case2 or case3)
        if k_end is None:
            break

        k_prev_start = k+1
        k = k_end+1

    # for showstopper: freeze j if case3
    j_next = j if reached_case3 else None

    return j_next, previous_branched_node


def ukkonen_v3(text: str) -> Node:
    # create implicit tree

    root = Node(is_root=True)
    root.suffix_link = root

    showstopper_activenode = None
    prev_was_showstopper = False

    global_end = GlobalEnd(-1)
    j_next: Optional[int] = None  # used for showstopper; if this value is set an integer,this values represents the j to start the extension from
    active_node = ActivePointer(root)
    prev_was_case3 = False

    for i in range(len(text)):
        global_end.increment()
        previous_branched_node = None  # for linking nodes

        if not prev_was_case3:
            suffixlink_activenode = SuffixLinkActivePointer(root)

        if prev_was_case3 and not prev_was_showstopper:
            showstopper_activenode = ShowstopperActivePointer(suffixlink_activenode)  #TODO check this # need this if you get a case3 in normal traversal

        prev_was_showstopper = False

        start = j_next if prev_was_case3 else i


        for j in range(start, i+1):
            # check the showstopper here
            # showstopper
            if prev_was_case3:
                prev_was_case3 = showstopper_extension()
                prev_was_showstopper = True

            # normal traversal
            else:
                # if previous extension was extended using showstopper -> use the active node created in it
                suffixlink_activenode = SuffixLinkActivePointer(showstopper_activenode=showstopper_activenode) if prev_was_showstopper else suffixlink_activenode

                # reset these showstopper related status
                prev_was_showstopper = False
                showstopper_activenode = None

                # actual extension
                j_next, previous_branched_node = do_extension(j, i, global_end, suffixlink_activenode, root, previous_branched_node, text)
                prev_was_case3 = j_next is not None

            # reached case 3 during comparison
            if prev_was_case3:
                break

    return root


class ShowstopperActivePointer(ActivePointer):
    """
    Technically, no need for this class. Just for clarity
    """

    def __init__(self, suffixlink_activenode):
        super().__init__()
        self.convert_from_suffixlink_activenode(suffixlink_activenode)
        self.j_start = None

    def convert_from_suffixlink_activenode(self, suffixlink_activenode: SuffixLinkActivePointer):
        self.node = suffixlink_activenode.node
        self.edge_idx = suffixlink_activenode.edge_idx
        self.length = suffixlink_activenode.length
        self.j_start = suffixlink_activenode.j_start

    def get_existing_idx_to_compare(self):
        # use this method for showstopper
        # includes the index of the embded char

        # -1 for inclusiveness and +1 for next char cancel out each other
        return self.node.start + self.length

    def increment_length(self):
        self.length += 1

    def do_need_to_goto_next_node(self) -> bool:
        return self.length == self.node.end - self.node.start + 1

    def update_jstart_for_new_node(self):
        self.j_start = self.j_start+self.length+1


def showstopper_extension(i: int, pointer: ShowstopperActivePointer,
                          previous_branched_node: Node, global_end: GlobalEnd, root: Node, text: str) \
        -> tuple[bool, Optional[Node], Optional[SuffixLinkActivePointer]]:
    """
    A: At embedded char -> case1 or case2-alt
    B: Between start ~ end -> case2 or case3
    modifies active node

    :param j:
    :param pointer:
    :param text:
    :return:
    """
    is_case_three = False
    current_node = pointer.node

    # TODO need to return suffixlink activenode
    #TODO check showstopper

    # A: previous turn finished checking all chars in the previous edge
    # -> in this turn, comparison happens at embedded char
    is_comparison_at_embedded = pointer.do_need_to_goto_next_node()
    if is_comparison_at_embedded:
        previous_node = current_node
        existing_idx = pointer.get_existing_idx_to_compare()
        current_node = current_node.get_edge_starting_with_char(text[existing_idx])

        # case 2-alt: branch at the root; or, brunch at an internal node
        if current_node is None and previous_node.is_root:



            # # active node update: +2 because: 1) both start and end are inclusive
            pointer.set_length(previous_node.end - previous_node.start + 1)
            previous_node.connect_edge(text[i], Node(start=i+1, end=global_end))
            previous_branched_node = branch_out(i, existing_idx, previous_node, pointer, previous_branched_node,
                                                root, global_end, text) # TODO cannot use branched node
            return is_case_three, previous_branched_node

        # case 2-alt
        if current_node is None and previous_node.is_root or current_node is None and not previous_node.is_leaf:

            # instantiating new suffixlink actvenode for next extension
            previous_node.connect_edge(text[i], Node(start=i+1, end=global_end))
            suffixlink_activenode = SuffixLinkActivePointer(previous_node)
            suffixlink_activenode.set_length(pointer.length)

            # updating previous_branched node (set it to the )
            previous_branched_node = previous_node


            return is_case_three, previous_branched_node, suffixlink_activenode

        # case 1: extension if there aren't other edges at a node (is leaf)
        if current_node is None and not previous_node.is_root and previous_node.is_leaf:
            suffixlink_activenode = SuffixLinkActivePointer(previous_node)
            suffixlink_activenode.set_length(pointer.length)  # until one index before the extension
            pointer.set_length(previous_node.end - previous_node.start + 1)  # update for suffix link active node
            previous_node.start = pointer.j_start
            previous_node.end = global_end

            # update current node and active length
            return is_case_three, previous_branched_node

        # case 3: same char at embedded
        if current_node is not None:
            pointer.update_node(current_node)
            pointer.set_length(0)
            pointer.update_jstart_for_new_node()
            is_case_three = True
            return is_case_three, previous_branched_node

    # B: there is still some characters left on the same edge as previous phase
    # comparison happens between start ~ end
    else:
        # case 3: same char
        existing_char_idx = pointer.get_existing_idx_to_compare()
        if text[i] == text[existing_char_idx]:
            pointer.increment_length()
            is_case_three = True
            return is_case_three, previous_branched_node

        # case 2: different char -> branch out
        previous_branched_node, suffixlink_pointer = branch_out(i, existing_char_idx, current_node, pointer, previous_branched_node, root, global_end, text)
        return is_case_three, previous_branched_node



