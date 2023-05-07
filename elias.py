from bitarray import bitarray
from math import ceil, log2
from bitarray.util import ba2int

from original_bitarray import BitArray


def elias_encode(num: int) -> BitArray:
    assert num > 0, "elias encode does not support 0 and negative numbers"

    components = []

    # convert num to binary
    current = decimal_to_bitarray(num)
    components.append(current)

    # start encoding backward
    component_length = len(current)
    while component_length > 1:
        component = decimal_to_bitarray(component_length-1)
        component.set_first_bit_to_zero()
        components.append(component)
        component_length = len(component)

    # concatenating the components
    encoded_num = components[-1]
    for i in range(len(components)-2, -1, -1):
        component = components[i]
        encoded_num.extend(component)

    # print("encoded num")
    # print(encoded_num)
    # print(type(encoded_num))
    return encoded_num




def decimal_to_bitarray(num: int) -> BitArray:
    result = BitArray()

    while num != 0:
        result.append(num & 1)
        num >>= 1

    result.reverse()
    return result


def elias_decode(bits: BitArray) -> tuple[int, BitArray]:
    if len(bits) == 1:
        return 1, BitArray()
    start, end = 0, 1

    while True:
        component = bits[start:end]
        # print("================")
        # print(component)
        if component[0] == 1:
            break

        component.set_first_bit_to_one()
        start = end
        end = start + component.to_decimal()+1
        # component = bits[start:end]

    remainder = bits[end:]  # note: this process is constant (see the implementation)

    return component.to_decimal(), remainder


if __name__ == "__main__":
    # print(elias_decode(elias_encode(100)))

    not_successful = []
    for test_num in range(10000, 100000):
        if test_num != elias_decode(elias_encode(test_num))[0]:
            not_successful.append(test_num)
    print(not_successful)