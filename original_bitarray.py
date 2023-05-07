from __future__ import annotations

class BitArray:
    """
    Bitarray, a wrapper class that represents a bitarray it is just an integer.
    note: it must remember the number of bits (i.e. how many 0s at the left)
    whenever something is added, increment num_bits

    -> when you write to file, ouput as byte object

    note: this class does not support iterator. use getitem instead

    note: instead of shifting multiple times do floor division (more efficinet)
    """
    def __init__(self, num: int):
        self.num = num
        self.n_bits = 0

    def __getitem__(self, item):
        # should support slicing to
        # when slicing, it should return another bitarray. be careful with n_bits
        pass

    def get_last(self):
        pass

    def reverse(self):
        """
        :return:
        """
        # create new num placeholder
        new_num = 0

        # take bits from the right and multiply by 10**len() -> add it to new_num

        pass

    def to_decimal(self):
        return self.num

    def extend(self, num: BitArray):
        """
        need to shift left self.num and then add the given bitarray
        :return:
        """
        pass

    def append(self):
        pass

    def get_as_byte(self):
        pass
