from bitarray import bitarray
from math import ceil, log2
from bitarray.util import ba2int


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


def elias_encode(num: int) -> bitarray:
    assert num > 0, "elias encode does not support 0 and negative numbers"

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
        # print("================")
        # print(component)
        if component[0] == 1:
            break

        component[0] = 1
        start = end
        end = start + bitarray_to_decimal(component)+1
        # component = bits[start:end]

    remainder = bits[end:]  # note: this process is constant (see the implementation)

    return bitarray_to_decimal(component), remainder


# if __name__ == "__main__":
#     # print(elias_decode(elias_encode(100)))
#
#     not_successful = []
#     for test_num in range(1, 1000000):
#         if test_num != elias_decode(elias_encode(test_num)):
#             not_successful.append(test_num)
#     print(not_successful)