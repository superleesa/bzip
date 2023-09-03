__author__ = "Satoshi Kashima"
__sid__ = 32678940
__description__ = "The implementation of Elias encoder and decoder"

from original_bitarray import BitArray


def elias_encode(num: int) -> BitArray:
    """
    Implementation of Elias encoder.

    :param num: a positive integer to encode
    :return: encoded text in BitArray
    """
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

    return encoded_num


def decimal_to_bitarray(num: int) -> BitArray:
    """
    Convert from decimal to bitarray
    :time complexity: O(num digits)
    """
    result = BitArray()

    while num != 0:
        result.append(num & 1)
        num >>= 1

    result.reverse()
    return result


def elias_decode(bits: BitArray) -> tuple[int, BitArray]:
    """
    Implementation of Elias decoder.

    :param bits: bitarray encoded with Elias encoder
    :return: the original integer, and any remained bitarray portion
    """
    if len(bits) == 1:
        return 1, BitArray()
    start, end = 0, 1

    while True:
        component = bits[start:end]
        if component[0] == 1:
            break

        component.set_first_bit_to_one()
        start = end
        end = start + component.to_decimal()+1

    remainder = bits[end:]  # note: this process is constant (see the implementation)

    return component.to_decimal(), remainder
