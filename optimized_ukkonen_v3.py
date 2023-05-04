from __future__ import annotations
from typing import Optional

# Ukkonen Version 3 - with trick1, 2, 4, and suffix link (without skip count)

MIN_ASCII, MAX_ASCII = 37, 126


def hash_ascii(char: str) -> int:
    assert MIN_ASCII <= ord(char) <= MAX_ASCII, "all characters must be in ascii value of 37-126"
    return ord(char) - MIN_ASCII


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

        # starting index j of an element compared to the edge
        self.j_start: Optional[int] = None

    def set_length(self, length: int):
        self.length = length  # includes the start and end of an edge

    def set_edge_idx(self, edge_idx: int):
        self.edge_idx = edge_idx

    def set_jstart(self, j_start):
        self.j_start = j_start


class SuffixLinkActivePointer(ActivePointer):
    def __init__(self, node: Optional[Node] = None, showstopper_activenode: ShowstopperActivePointer = None):
        super().__init__()

        if showstopper_activenode and node or not showstopper_activenode and not node:
            raise ValueError("only one of showstopper and node should be used to instantiate suffixlink activenode")

        if showstopper_activenode is not None:
            self.convert_from_showstopper_activenode(showstopper_activenode)

        if node is not None:
            self.node = node
            self.length = node.end - node.start + 1

    def convert_from_showstopper_activenode(self, showstopper_activenode: ShowstopperActivePointer):
        self.node = showstopper_activenode.node
        self.edge_idx = showstopper_activenode.edge_idx
        self.length = showstopper_activenode.length

    def update_node(self, node: Node):
        self.node = node


class Node:
    """
    The first character of each edge is embedded in previous node to enable accessing into edges in a constant time.
    """

    def __init__(self, start=None, end=None, is_root=False):
        self.start: Optional[int] = start  # the index of the start character of an edge (inclusive)
        self.end: Optional[int] = end  # the index of the last character (inclusive)

        # outward edges from this node
        # each index represents the starting character of an outward edge
        # this is just a reference table - do not use this for storing character
        self.edges: list[Optional[Node]] = [None] * (MAX_ASCII - MIN_ASCII + 1)

        self.is_root = is_root

        # used to distinguish case1 vs. case2-alt
        self.is_leaf = True  # set to false when brunching out

        # for suffix link
        self.suffix_link: Optional[Node] = None

    def connect_edge(self, first_char: str, node: Node) -> None:
        self.edges[hash_ascii(first_char)] = node

    def get_node_starting_with_char(self, char: str) -> Optional[Node]:
        return self.edges[hash_ascii(char)]


class GlobalEnd:
    def __init__(self, i):
        self.i = i

    def increment(self):
        self.i += 1

    def __str__(self):
        return str(self.i)


def branch_out(inserting_char_idx: int, existing_char_idx: int, current_node: Node, active_node: ActivePointer,
               previous_branched_node: Node,
               root: Node, global_end: GlobalEnd, text: str):
    """
    Makes extension to the current node and resolves pending suffix link from the previous extension
    Modifies the attributes of current node and active node

    :param inserting_char_idx:
    :param existing_char_idx:
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
    existing_branch = Node(start=existing_char_idx, end=global_end)
    current_node.end = existing_char_idx - 1
    current_node.is_leaf = False
    inserting_branch = Node(start=inserting_char_idx, end=global_end)
    current_node.connect_edge(text[existing_char_idx], existing_branch)
    current_node.connect_edge(text[inserting_char_idx], inserting_branch)

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
                 active_node: ActivePointer, root: Node, previous_branched_node: Optional[Node], text: str) \
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

    for existing_idx in range(current_node.start, end + 1):

        # case 2 - branch out
        if text[existing_idx] != text[k]:
            return k, reached_case3, branch_out(k, existing_idx, current_node, active_node, previous_branched_node,
                                                root, global_end, text)

        # case 3 - the one already exists longer: stop
        if k == i:
            reached_case3 = True
            return None, reached_case3, previous_branched_node

        k += 1

    # extension needs to be continued
    return k, reached_case3, previous_branched_node


def do_extension(j: int, i: int, global_end: GlobalEnd, active_node: SuffixLinkActivePointer, root: Node,
                 previous_branched_node: Optional[Node], text: str) -> tuple[Optional[int], Node]:
    """
    Iterates through the nodes to find where the current substring should go
    changes attributes of active node inside
    :param active_node:
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

    # TODO need to check j_start for the active node

    current_node: Optional[Node] = root
    k: int = j  # pointer to the index being compared of a current substring text[j:i+1]
    reached_case3: bool = False
    active_edge_idx = None

    # check active node to determine if we can use suffix link
    if active_node.node.suffix_link != root:
        # suffix link points to a node that is not node -> does not need to traverse naively
        k = active_node.j_start
        current_node = active_node.node.suffix_link
        active_edge_idx = active_node.edge_idx

        # TODO get length too for skip count

    while True:
        previous_node: Node = current_node  # the previous node the current substring visited
        # if we have an effective active node, it stores edge idx already
        edge_idx = active_edge_idx or hash_ascii(text[k])
        active_edge_idx = None
        current_node = previous_node.edges[edge_idx]

        # case 2-alt: branch at the root; or, brunch at an internal node
        if current_node is None and previous_node.is_root or current_node is None and not previous_node.is_leaf:
            # active length update
            active_node.set_length(previous_node.end - previous_node.start + 1)

            # previous_branched_node related procedure
            previous_branched_node = current_node

            # create new node and connect it
            previous_node.connect_edge(text[k], Node(start=k, end=global_end))
            break

        # case 1: extension if there aren't other edges at a node
        if current_node is None and not previous_node.is_root and previous_node.is_leaf:
            # active length update
            active_node.set_length(previous_node.end - previous_node.start + 1)

            # update the start&end to extend existing edge
            previous_node.start = k_prev_start  # TODO do something with k_prev_start
            previous_node.end = global_end
            break

        # active node update
        active_node.update_node(previous_node)
        active_node.set_edge_idx(hash_ascii(text[k]))
        active_node.set_jstart(k)

        # actual comparison
        k_end, reached_case3, previous_branched_node = \
            compare_edge(k, current_node, i, global_end, active_node, root, previous_branched_node, text)

        # reached the end already during the actual comparison(case2 or case3)
        if k_end is None:
            break

        k_prev_start = k + 1
        k = k_end + 1

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
    j_next: Optional[
        int] = None  # used for showstopper; if this value is set to an integer,this values represents the j to start the extension from
    suffixlink_activenode = SuffixLinkActivePointer(root)
    prev_was_case3 = False

    for i in range(len(text)):
        global_end.increment()
        previous_branched_node = None  # for linking nodes

        # comes back here in four ways (requires two variables: prev_was_case3, prev_was_showstopper)
        # 1) no case3 in prev phase -> going to next phase normally
        # 2) found case3 in the last extension of the previous phase in normal during normal traversal-> start showstopper
        # 3) prev was case3 and was already in showstopper (i.e. got case3 in twice a row)
        # 4) prev was not case3 and was in showstopper (i.e. during showstopper, finally reached case1 or case2)

        # preparation for showstopper
        if prev_was_case3 and not prev_was_showstopper:
            # found case3 during traversal -> requires initialization of showstopper pointer
            showstopper_pointer = ShowstopperActivePointer(root, j_next, text[j_next])

        # preparation for normal traversal
        if not prev_was_case3:
            # just start with the root
            suffixlink_activenode.update_node(root)

        start = j_next if prev_was_case3 else i

        for j in range(start, i + 1):

            # check the showstopper here
            # showstopper
            if prev_was_case3:
                prev_was_case3 = False  # reinitialize

                prev_was_case3, previous_branched_node, suffixlink_activenode = showstopper_extension(i,
                                                                                                      showstopper_pointer,
                                                                                                      previous_branched_node,
                                                                                                      global_end, root,
                                                                                                      text)
                prev_was_showstopper = True


            # normal traversal
            else:
                prev_was_case3 = False  # reinitialize

                # if previous extension was extended using showstopper -> use the active node created in it
                # else, use the active node from the previous turn to make skips in this turn
                if prev_was_showstopper:
                    suffixlink_activenode = SuffixLinkActivePointer(showstopper_activenode=showstopper_activenode)
                    prev_was_showstopper = False

                # reset these showstopper related status
                prev_was_showstopper = False
                showstopper_activenode = None

                # actual extension
                # note: no need to change j_next until we pass through all the consecutive case3s
                j_next, previous_branched_node = do_extension(j, i, global_end, suffixlink_activenode, root,
                                                              previous_branched_node, text)
                prev_was_case3 = j_next is not None

            # reached case 3 during comparison/showstopper -> trigger showstopper
            if prev_was_case3:
                break

    return root


class ShowstopperActivePointer(ActivePointer):
    """
    Technically, no need for this class. Just for clarity
    """

    # def __init__(self, suffixlink_activenode):
    #     super().__init__()
    #     self.convert_from_suffixlink_activenode(suffixlink_activenode)

    def __init__(self, root: Node, j_start: int, char: str):
        """
        can be used when there was a case3 during the traversal -> the first time using the showstopper
        :param root: must be the root node
        """
        super().__init__()
        self.node = root
        self.length = 1
        self.j_start = j_start
        self.edge_idx = hash_ascii(char)
        pass

    def convert_from_suffixlink_activenode(self, suffixlink_activenode: SuffixLinkActivePointer):
        self.node = suffixlink_activenode.node
        self.edge_idx = suffixlink_activenode.edge_idx
        self.j_start = suffixlink_activenode.j_start
        self.length = 0

        # don't use length (it's invalid)

    def get_existing_idx_to_compare(self):
        # use this method for showstopper
        # includes the index of the embded char

        # -1 for inclusiveness and +1 for next char cancel out each other
        assert not self.node.is_root, "this method shouldn't be used for root node"
        return self.node.start + self.length

    def increment_length(self):
        self.length += 1

    def do_need_to_goto_next_node(self) -> bool:
        if self.node.is_root:
            return True

        assert self.length <= self.node.end - self.node.start + 1, "the visited legnth should always be smaller or equal to the actual length of the edge"
        return self.length == self.node.end - self.node.start + 1

    def point_to_next_node(self, node: Node):
        self.j_start = self.j_start + self.node.end - self.node.start + 1
        self.node = node
        self.length = 0


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
    suffixlink_activenode = None

    # TODO need to return suffixlink activenode
    # TODO check showstopper

    # A: previous turn finished checking all chars in the previous edge
    # -> in this turn, comparison happens at embedded char

    if pointer.do_need_to_goto_next_node():
        previous_node = current_node
        current_node = current_node.get_node_starting_with_char(text[i])

        # case 2-alt: branch at the root; or, brunch at an internal node
        if current_node is None and previous_node.is_root or current_node is None and not previous_node.is_leaf:
            # instantiating new suffixlink activenode for next extension
            previous_node.connect_edge(text[i], Node(start=i, end=global_end))
            suffixlink_activenode = SuffixLinkActivePointer(previous_node)

            # updating previous_branched node (set it to the new_branch)
            previous_branched_node.suffix_link = previous_node
            previous_branched_node = previous_node

            return is_case_three, previous_branched_node, suffixlink_activenode

        # case 1: extension if there aren't other edges at a node (is leaf)
        if current_node is None and not previous_node.is_root and previous_node.is_leaf:
            suffixlink_activenode = SuffixLinkActivePointer(previous_node)

            previous_node.start = pointer.j_start
            previous_node.end = global_end

            # no change in previous_branched node (because there is no branching in case1)

            # update current node and active length
            return is_case_three, previous_branched_node, suffixlink_activenode

        # case3
        if current_node is not None:
            pointer.point_to_next_node(previous_node)
            pointer.set_edge_idx(hash_ascii(text[i]))
            # goes to the below block

    # B: there is still some characters left on the same edge as previous phase
    # comparison happens between start ~ end

    # case 3: same char
    existing_char_idx = pointer.get_existing_idx_to_compare()
    if text[i] == text[existing_char_idx]:
        pointer.increment_length()
        is_case_three = True
        return is_case_three, previous_branched_node, suffixlink_activenode

    # case 2: different char -> branch out
    if text[i] != text[existing_char_idx]:
        previous_branched_node = branch_out(i, existing_char_idx, current_node, pointer,
                                            previous_branched_node, root, global_end, text)
        suffixlink_activenode = SuffixLinkActivePointer(current_node)
        return is_case_three, previous_branched_node, suffixlink_activenode

    raise ValueError("shouldn't come here")
