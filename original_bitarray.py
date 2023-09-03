from __future__ import annotations

__author__ = "Satoshi Kashima"
__sid__ = 32678940
__description__ = "The implementation of an original BitArray class"


from typing import Optional

class BitArray:
    """
    Bitarray, a wrapper class that represents a bitarray. Internally, it is just an integer.

    note: it stores the number of bits as well to keep track of how many leading 0s
    note: this class does not support iterator. use getitem instead
    """

    def __init__(self, num: int = 0, n_bits: int = 0) -> None:
        assert not (num is None and n_bits is not None or num is not None and n_bits is None), "both of them should be present, or both of them should not be present"
        self.num: Optional[int] = num
        self.n_bits: Optional[int] = n_bits

    def __getitem__(self, item):
        """
        Supports both indexing and slicing
        note: we assume that bit shifting is a constant time operation (in reality it depends on cpu;however, the below
         operations can easily be replaced by floor divisions and mod operations which are constant)
        """
        # should support slicing too
        if isinstance(item, int):
            if item < -self.n_bits or item >= self.n_bits:
                raise IndexError('index out of range')
            if item < 0:
                raise ValueError("does not support negative index")
            return (self.num >> (self.n_bits - item - 1)) & 1
        if isinstance(item, slice):
            # note: the stop here is exclusive
            start, stop, step = item.indices(self.n_bits)
            if step != 1:
                raise ValueError("step not supported")

            if start >= stop:
                return ValueError("start should be bigger than stop")

            if stop > self.n_bits:
                raise ValueError("stop value too big")

            mask = (1 << (stop - start)) - 1
            sliced_num = (self.num >> (len(self) - stop)) & mask
            sliced_n_bits = stop - start
            return BitArray(sliced_num, n_bits=sliced_n_bits)

    def __len__(self) -> int:
        return self.n_bits

    def reverse(self) -> None:
        """
        Reverse the current bits.
        """
        # create new num placeholder
        new_num = 0

        # take bits from the right and multiply by 2*i -> add it to new_num
        for i in range(len(self)):
            # ensure that msb in the original bits will be multiplies by 2 more times
            new_num <<= 1

            # adds the ith bit to new num
            new_num |= (self.num >> i) & 1

        self.num = new_num

    def to_decimal(self) -> int:
        return self.num

    def extend(self, num: BitArray) -> None:
        """
        Simulate the extension of bitarray.
        Internally, it simply adds the given number to self.num
        """
        # shift left self.num and then add the given bitarray
        self.num <<= len(num)
        self.num |= num.num
        self.n_bits += len(num)

    def append(self, bit: int):
        assert bit == 0 or bit == 1, "bit must be 0 or 1"
        self.num <<= 1
        self.num |= bit
        self.n_bits += 1

    def tobytes(self):
        # ensure that you only use this method if the first bit starts from 1. else, it will lose all leading 0s.
        num_bytes = (self.n_bits + 7) // 8
        byte_str = self.num.to_bytes(num_bytes, byteorder='big')
        return bytes(byte_str)

    def set_first_bit_to_zero(self):
        """
        set the first bit of the bitarray to 0.
        """
        mask = 1 << (self.n_bits - 1)
        self.num &= ~mask

    def set_first_bit_to_one(self):
        """
        Set the first bit of the bitarray to 1.
        """
        mask = 1 << (self.n_bits - 1)
        self.num |= mask

    def __str__(self):
        return bin(self.num)[2:].zfill(self.n_bits)
