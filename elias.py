from bitarray import bitarray
from math import ceil, log2
from bitarray.util import ba2int

class OriginalBitarray:
    def __init__(self):
        pass

    def __setitem__(self, key, value):
        pass

    def reverse(self):
        # traverse through the int backward -> use AND and SHIFT operators
        # use iterator to do this
        pass

    def append(self):
        # shift left -> add 1 or 0
        pass


class ByteIterator:
    def __init__(self, bits: int):
        self.bits = bits
        self.i = 0

        self.max_i = 7

    def __iter__(self):
        return self

    def __next__(self):
        self.i += 1
        if self.i > self.max_i:
            raise StopIteration
        return (self.bits >> self.i) & 1


def elias_encode(num: int):
    components = []

    # convert num to binary
    current = decimal_to_bitarray(num)
    components.append(current)

    # start encoding backward
    component_length = len(current)
    while component_length > 1:
        component = decimal_to_bitarray(component_length-1)
        component[0] = 0
        components.append(component)
        component_length = len(component)

    # concatenating the components
    encoded_num = components[-1]
    for i in range(len(components)-2, -1, -1):
        component = components[i]
        encoded_num.extend(component)

    return encoded_num


def decimal_to_bitarray(num: int) -> bitarray:
    result = bitarray()

    while num != 0:
        result.append(num%2)
        num = num // 2

    result.reverse()
    return result


def bitarray_to_decimal(bits: bitarray) -> int:
    return ba2int(bits)


def elias_decode(bits: bitarray):
    start, end = 0, 1

    while True:
        component = bits[start:end]
        print("================")
        print(component)
        if component[0] == 1:
            break

        component[0] = 1
        start = end
        end = start + bitarray_to_decimal(component)+1
        component = bits[start:end]

    return bitarray_to_decimal(component)