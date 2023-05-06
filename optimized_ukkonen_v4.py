from __future__ import annotations
from typing import Optional, Union
# from main import getinfo_tree
from pprint import pprint
from abc import ABC


def getinfo_tree(root):
    return getinfo_tree_aux(root)


def getinfo_tree_aux(node):
    result = [(node.start, str(node.end)), {}]

    for idx, connected_node in enumerate(node.edges):
        if isinstance(connected_node, Node):
            result[1][hashed_ascii_to_char(idx)] = getinfo_tree_aux(connected_node)

    return result


# Ukkonen Version 4 - with all tricks and suffix link

MIN_ASCII, MAX_ASCII = 37, 126


def hash_ascii(char: str) -> int:
    assert MIN_ASCII <= ord(char) <= MAX_ASCII or char == "$", "all characters must be in ascii value of 37-126, or '$'"

    if char == "$":
        return 0
    else:
        return ord(char) - MIN_ASCII + 1


def hashed_ascii_to_char(idx):
    if idx == 0:
        return "$"
    else:
        return chr(idx + MIN_ASCII - 1)


class ActivePointer(ABC):
    """
    if self.node = root, ignore edge and length and start the comparison from j

    Can be used in two ways:
    1) to move from one extension to another quickly using suffix link; active node points to the last internal node visited in a traversal
    2) for showstopper; active node points to the last character visited in the previous iteration
    """

    def __init__(self):
        self.node: Optional[Node] = None
        self.edge_idx: Optional[int] = None
        self.length: Optional[int] = None

        # starting index j of an element compared to the edge
        self.j_start: Optional[int] = None

        # # number of chracters traversed so far along the reminder
        # self.traversed_length: int = 0

    def set_length(self, length: int) -> None:
        self.length = length  # includes the start and end of an edge

    def set_edge_idx(self, edge_idx: int) -> None:
        self.edge_idx = edge_idx

    def set_jstart(self, j_start) -> None:
        self.j_start = j_start

    def update_to_next_node(self, edge_idx: int, k: int) -> None:
        """
        Create a new node out of a node
        Input does not require next node itself because it can be obtained from the previous node.edge_idx
        Used by both the suffix link pointer and showstopper pointer.

        :param edge_idx: the hashed value for he first character of the edge
        :param k: the index of the first character for the selected edge. this should be the index of the inserting one
        (not existing one)
        :return:
        """
        assert edge_idx is not None, "edge_idx shouldn't be none"
        assert k is not None, "k shouldn't be none"

        # if self.node.is_root:
        #     self.edge_idx = edge_idx

        print(self.node.get_node_using_idx(self.edge_idx))

        assert self.node.get_node_using_idx(self.edge_idx).get_node_using_idx(edge_idx) is not None, \
            "ensure that there is an existing edge out before updating active node to it"
        self.node = self.node.get_node_using_idx(self.edge_idx)
        self.j_start = k
        self.edge_idx = edge_idx
        self.length = 0


class SuffixLinkActivePointer(ActivePointer):
    def __init__(self, node: Node, j_start: int, edge_idx: Optional[int] = None, length: int = 0) -> None:
        super().__init__()

        if edge_idx is None:
            assert node.is_root, "node should be root when edge_idx is undefined"

        self.node = node
        self.edge_idx = edge_idx
        self.length = length
        self.j_start = j_start

        self.is_initial = True

    def _reinitialize_from_root(self, root: Node) -> None:
        """
        this method does not update the edge_idx yet since at the time of creation of pointer,
        we don't know which character comes after. Therefore, later, edge_idx must be set seaparately.
        The update_to_next_node method handles this
        :param root:
        :return:
        """
        assert root.is_root, "node must be root to use this method"
        self.node = root
        self.edge_idx = None
        self.length = 0

    def reinitialize(self) -> None:
        linked_node = self.node.suffix_link
        if linked_node.is_root:
            self._reinitialize_from_root(linked_node)
        else:
            # suffix link pointed to somewhere not root
            self.node = linked_node

        self.is_initial = True

    def does_suffixlink_points_to_root(self) -> bool:
        return self.node.suffix_link.is_root

    def __str__(self) -> str:
        if self.edge_idx is None:
            return "edge_idx is None"

        pointed_outgoing_edge = self.node.get_node_using_idx(self.edge_idx)
        start = pointed_outgoing_edge.start
        end = pointed_outgoing_edge.get_end()
        return str((start, end))


class Node:
    """
    The first character of each edge is embedded in previous node to enable accessing into edges in a constant time.
    """

    def __init__(self, start: int, end: Union[int, GlobalEnd], is_root: bool = False) -> None:
        self.start: Optional[int] = start  # the index of the start character of an edge (inclusive)
        self.end: Union[Optional[int], GlobalEnd] = end  # the index of the last character (inclusive)

        if not is_root:
            assert start <= (end.i if isinstance(end, GlobalEnd) else end), \
                "start should always be smaller than or equal to end"

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

    def get_node_using_starting_char(self, char: str) -> Optional[Node]:
        return self.edges[hash_ascii(char)]

    def get_node_using_idx(self, edge_idx: int) -> Optional[Node]:
        return self.edges[edge_idx]

    def set_start(self, start: int) -> None:
        """
        ensure that only start is updated when using this function (not end). the assertion does not hold if not so
        :param start:
        :return:
        """
        assert start is not None, "start shouldn't be none"

        assert start <= self.get_end(), "start should be smaller than or equal to the end"
        self.start = start

    def set_end(self, end: Union[int, GlobalEnd]) -> None:
        """
        ensure that only end is updated when using this function (not start). the assertion does not hold if not so
        :param end:
        :return:
        """
        assert end is not None, "end shouldn't be none"
        assert self.get_end() >= self.start, "end should be bigger than or equal to start"

        self.end = end

    def set_start_and_end(self, start: int, end: Union[int, GlobalEnd]) -> None:
        assert start is not None and end is not None, "both start and end shouldn't be none"
        assert start <= self.get_end(), "start should be smaller than or equal to end"

        self.start = start
        self.end = end

    def resolve_suffixlink(self, previous_branched_node: Optional[Node], root: Node) -> Node:
        """
        resolve pending suffix link AND connect this node to the root node temporality.
        Returns this node as the new previous branched node.

        :param previous_branched_node: a node branched in the previous extension (of the same phase)
        :param root: the root node
        :return: this node itself, as the new previous_branched_node
        """
        assert root.is_root, "the second argument must be the root node"

        # suffix link related procedures
        self.suffix_link = root  # connect the branched node to root temporarily
        # RESOLVE: connect the previously branched node in a previous extension to the branched node
        if previous_branched_node is not None:
            previous_branched_node.suffix_link = self

        return self

    def remove_edge(self, first_char: str) -> None:
        edge_idx = hash_ascii(first_char)
        self.edges[edge_idx] = None

    def get_end(self) -> int:
        return self.end.i if isinstance(self.end, GlobalEnd) else self.end

    def __str__(self) -> str:
        return str((self.start, self.end, self.edges, self.is_root, self.is_leaf))


class GlobalEnd:
    def __init__(self, i) -> None:
        self.i = i

    def increment(self) -> None:
        self.i += 1

    def __str__(self) -> str:
        return str(self.i)


def branch_out(inserting_char_idx: int, existing_char_idx: int, current_node: Node, previous_node: Node,
               previous_branched_node: Node, active_node: ActivePointer,
               root: Node, global_end: GlobalEnd, text: str) -> Optional[Node]:
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
    # removing the curret edge from the previous node
    previous_node.remove_edge(text[current_node.start])

    # creating an inner node that connects the previous node and two child nodes for the existing and inserting chars
    internal_node = Node(current_node.start, existing_char_idx - 1)
    internal_node.is_leaf = False

    # treat current node as the branch for existing branch; connect this to the inner node
    current_node.set_start(existing_char_idx)
    current_node.is_leaf = False
    internal_node.connect_edge(text[existing_char_idx], current_node)

    # create an edge for inserting char and connect it to the inner node
    inserting_node = Node(start=inserting_char_idx, end=global_end)
    internal_node.connect_edge(text[inserting_char_idx], inserting_node)

    assert text[inserting_char_idx - 1] == text[existing_char_idx - 1], \
        "at least one char of the splitting edge should be the same"

    # finally, connect the previous node to the inner node
    previous_node.connect_edge(text[internal_node.start], internal_node)

    # updating the length of the current active node
    active_node.set_length(internal_node.get_end() - internal_node.start + 1)

    # resolve pending suffix links
    previous_branched_node = internal_node.resolve_suffixlink(previous_branched_node, root)

    return previous_branched_node


def compare_character(k: int, i: int, existing_idx: int, current_node: Node, previous_node: Node,
                      previous_branched_node: Optional[Node],
                      active_node: SuffixLinkActivePointer,
                      global_end: GlobalEnd, root: Node, text: str) -> tuple[Optional[int], bool, Optional[Node]]:

    # case 2 - branch out
    if text[existing_idx] != text[k]:
        return None, False, branch_out(k, existing_idx, current_node, previous_node, previous_branched_node,
                                       active_node, root, global_end, text)

    # case 3 - the one already exists longer: stop
    if k == i:
        reached_case3 = True
        active_node.set_length(current_node.get_end() - current_node.start + 1)
        return None, True, previous_branched_node

    # should go to next iteration (if allowed)
    return k, False, previous_branched_node


def compare_edge(k: int, i: int, current_node: Node, previous_node: Node, previous_branched_node: Optional[Node],
                 active_node: SuffixLinkActivePointer, global_end: GlobalEnd, root: Node, text: str) \
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
    end: int = current_node.get_end()

    for existing_idx in range(current_node.start, end + 1):

        k, reached_case3, previous_branched_node = compare_character(k, i, existing_idx,
                                                                     current_node, previous_node,
                                                                     previous_branched_node, active_node,
                                                                     global_end, root, text)

        if k is None:
            break

        k += 1

    # requires a further traversal
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
    active_edge_idx: Optional[int] = None

    # check active node to see if we can use suffix link
    can_use_suffixlink = not active_node.does_suffixlink_points_to_root()
    if can_use_suffixlink:
        print("uses suffix link active node")
        # suffix link points to a node that is not node -> does not need to traverse naively
        k = active_node.j_start
        current_node = active_node.node.suffix_link
        active_edge_idx = active_node.edge_idx

        # print("skipped to current node: ", current_node.start, current_node.end)
        # print("skipped to k value of", k)
        # TODO get length too for skip count
        length_required_to_traverse = active_node.length
        assert length_required_to_traverse is not None and length_required_to_traverse != 0, "length should be " \
                                                                                             "neither None nor 0 "
        length_traversed = 0

    # ensures that the active node starts from where the previous active node linked to
    active_node.reinitialize()

    if active_node.node.is_root:
        active_node.set_edge_idx(hash_ascii(text[k]))

    # important invariance here (">" means is parent):
    # active_node >= previous > current
    while True:
        # if edge_idx already defined by the active_node -> use it
        edge_idx = active_edge_idx or hash_ascii(text[k])
        active_edge_idx = None

        previous_node: Node = current_node  # the previous node the current substring visited
        current_node = previous_node.edges[edge_idx]

        # case 2-alt: branch at the root; or, brunch at an internal node
        if current_node is None and previous_node.is_root or current_node is None and not previous_node.is_leaf:
            # active length update
            active_node.set_length(previous_node.get_end() - previous_node.start + 1)

            # previous_branched_node related procedure
            previous_branched_node = previous_node.resolve_suffixlink(previous_branched_node, root)

            # create new node and connect it
            previous_node.connect_edge(text[k], Node(start=k, end=global_end))
            previous_node.is_leaf = False  # only useful when the input was root and i == 0
            break

        assert current_node is not None, "current node should not be none"

        # active node update: it's here because active node should only be updated when there is something to traverse
        # for the first iteration, active node won't be updated since it hasn't traversed any edges yet (only found that there is an edge)
        if not active_node.is_initial:
            active_node.update_to_next_node(edge_idx, k)
        else:
            active_node.is_initial = False

        # SKIP COUNT --> if suffixlink being used -> can skip using skip count
        if can_use_suffixlink:
            # check if we can skip
            length_of_this_edge = current_node.get_end() - current_node.start + 1
            can_skip = length_traversed + length_of_this_edge <= length_required_to_traverse

            # if can skip
            if can_skip:
                k += length_of_this_edge
                length_traversed += length_of_this_edge
                continue

            # if cannot skip i.e. remainder ends in the current edge
            if not can_skip:
                # calculate exactly at which index change has to be made
                offset = length_required_to_traverse - length_traversed
                existing_char_idx = current_node.start + offset
                inserting_char_idx = k + offset

                # case 2
                _, reached_case3, previous_branched_node = \
                    compare_character(inserting_char_idx, i, existing_char_idx, current_node,
                                      previous_node, previous_branched_node, active_node, global_end, root, text)
                break

        # --> did not use suffix link -> requires actual comparison
        k_end, reached_case3, previous_branched_node = \
            compare_edge(k, i, current_node, previous_node, previous_branched_node, active_node, global_end, root, text)

        # reached the end already during the actual comparison(case2 or case3) -> does not require a furhter traversal
        if k_end is None:
            break

        k = k_end

    # for showstopper: freeze j if case3
    j_next = j if reached_case3 else None

    return j_next, previous_branched_node


def ukkonen_v3(text: str) -> Node:
    # create implicit tree

    root = Node(0, -1, is_root=True)
    root.suffix_link = root  # root's suffix link points back to itself

    showstopper_activenode = None
    prev_was_showstopper = False

    global_end = GlobalEnd(-1)
    j_next: Optional[int] = None  # used for showstopper; represent the j to start the extension from
    prev_was_case3 = False

    for i in range(len(text)):
        pprint(getinfo_tree(root))
        print("=================next iteration========================")
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
            suffixlink_activenode = SuffixLinkActivePointer(root, 0)

        start = j_next if prev_was_case3 else i

        for j in range(start, i + 1):
            print("inner loop: ", j, i)

            # check the showstopper here
            # showstopper
            if prev_was_case3:
                print("goes to: showstopper")
                prev_was_case3, previous_branched_node, suffixlink_activenode = showstopper_extension(i,
                                                                                                      showstopper_pointer,
                                                                                                      previous_branched_node,
                                                                                                      global_end, root,
                                                                                                      text)
                prev_was_showstopper = True


            # normal traversal
            else:
                print("goes to normal traversal", j, i)

                prev_was_showstopper = False

                # actual extension
                # note: no need to change j_next until we pass through all the consecutive case3s
                j_next, previous_branched_node = do_extension(j, i, global_end, suffixlink_activenode, root,
                                                              previous_branched_node, text)
                prev_was_case3 = j_next is not None

            # reached case 3 during comparison/showstopper -> trigger showstopper
            if prev_was_case3:
                break

    pprint(getinfo_tree(root))
    return root


class ShowstopperActivePointer(ActivePointer):
    """
    pointer for showstopper
    """

    def __init__(self, root: Node, j_start: int, starting_char: str) -> None:
        """
        can be used when there was a case3 during the traversal -> the first time using the showstopper
        :param root: must be the root node
        """
        assert root.is_root, "showstopper should only be instantiated from a root node (because of trick1)"
        assert starting_char is not None, "at least one case3 must be occured previously; this char should be inputted"

        super().__init__()
        self.node = root
        self.length = 1
        self.j_start = j_start
        self.edge_idx = hash_ascii(starting_char)
        pass

    def get_existing_idx_to_compare(self) -> int:
        # use this method for showstopper
        # assert not self.node.is_root, "this method shouldn't be used for root node"

        pointed_outgoing_edge = self.node.get_node_using_idx(self.edge_idx)
        start = pointed_outgoing_edge.start
        return start + self.length

    def increment_length(self) -> None:
        self.length += 1

    def do_need_to_goto_next_node(self) -> bool:
        # this node is not properly pointed yet

        assert self.edge_idx is not None and self.length is not None, "showstopper pointer must always have edge_idx and length"

        pointed_outgoing_node = self.node.get_node_using_idx(self.edge_idx)
        start = pointed_outgoing_node.start
        end = pointed_outgoing_node.get_end()  # check for global end

        assert self.length <= end - start + 1, "the visited legnth should always be smaller or equal to the actual length of the edge"
        return self.length == end - start + 1

    def get_next_node_for_branch_out(self) -> Node:
        return self.node.get_node_using_idx(self.edge_idx)

    def __str__(self):
        pointed_outgoing_edge = self.node.get_node_using_idx(self.edge_idx)
        start = pointed_outgoing_edge.start
        end = pointed_outgoing_edge.get_end()
        return start, end


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
    suffixlink_activenode = None

    if not pointer.do_need_to_goto_next_node():
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
            previous_branched_node = branch_out(i, existing_char_idx, pointer.get_next_node_for_branch_out(),
                                                pointer.node,
                                                previous_branched_node, pointer, root, global_end, text)
            suffixlink_activenode = SuffixLinkActivePointer(pointer.node, pointer.j_start, pointer.edge_idx,
                                                            pointer.length)
            return is_case_three, previous_branched_node, suffixlink_activenode

    # A: previous turn finished checking all chars in the previous edge
    # -> in this turn, comparison happens at embedded char
    if pointer.do_need_to_goto_next_node():
        edge_idx = hash_ascii(text[i])

        previous_node = pointer.node.get_node_using_idx(pointer.edge_idx)
        current_node = previous_node.get_node_using_starting_char(text[i])

        # case 2-alt: branch at the root; or, brunch at an internal node
        if current_node is None and previous_node.is_root or current_node is None and not previous_node.is_leaf:
            # update active length
            pointer.set_length(previous_node.get_end() - previous_node.start + 1)

            previous_node.connect_edge(text[i], Node(start=i, end=global_end))

            # instantiating new suffixlink activenode for next extension
            suffixlink_activenode = SuffixLinkActivePointer(pointer.node, pointer.j_start, pointer.edge_idx,
                                                            pointer.length)

            # updating previous_branched node (set it to the new_branch)
            previous_branched_node = previous_node.resolve_suffixlink(previous_branched_node, root)

            return is_case_three, previous_branched_node, suffixlink_activenode

        # case 3: same char
        if current_node is not None:
            pointer.update_to_next_node(edge_idx, i)
            pointer.increment_length()
            is_case_three = True
            return is_case_three, previous_branched_node, suffixlink_activenode

        # case3
        # if current_node is not None:
        #     pass
        # goes to the below block

    raise ValueError("shouldn't come here")
