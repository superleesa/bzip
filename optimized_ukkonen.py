from naive_ukkonen import MIN_ASCII, MAX_ASCII, hash_ascii, Node, getinfo_tree


def ukkonen(text: str) -> Node:
    root = Node(is_root=True)

    for i in range(len(text)):
        for j in range(i + 1):

            # iterates through the nodes to find where the current substring should go
            current_node = root
            k = j  # pointer to the index being compared of a current substing text[j:i+1]
            while True:
                # print("comes here")
                previous_node = current_node
                current_node = previous_node.link[hash_ascii(text[k])]

                # case 1 (reaches a leaf -> needs extension): occurs at root (the first iteration)
                if current_node is None and previous_node.is_root:
                    previous_node.link[hash_ascii(text[j])] = Node(start=j + 1, end=i)
                    break

                # case 1: occurs at middle (after at least 1 edge=branch=iteration)
                # part of case 2 also applies here (brunch out from an existing node)
                if current_node is None and not previous_node.is_root:
                    previous_node.start = starting_k
                    previous_node.end = i
                    break

                reaches_end = False
                starting_k = k + 1
                for l in range(current_node.start, current_node.end + 1):
                    # case 2 - branch out
                    if text[l] != text[k]:
                        # create two new nodes: the existing and the one inserting
                        # put them in node.link of the current node-> you hash first to find where to put
                        # print("==========")
                        existing_branch = Node(start=l + 1, end=current_node.end)
                        current_node.end = l - 1
                        inserting_branch = Node(start=k + 1, end=i)
                        current_node.link[hash_ascii(text[l])] = existing_branch
                        current_node.link[hash_ascii(text[k])] = inserting_branch
                        reaches_end = True
                        break

                    # case 3 - the one already exists longer: stop
                    if k == i:
                        reaches_end = True
                        break

                    k += 1  # update k

                if reaches_end:
                    break

    return root