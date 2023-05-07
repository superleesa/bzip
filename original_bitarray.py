from __future__ import annotations


class BitArray:
    """
    Bitarray, a wrapper class that represents a bitarray it is just an integer.
    note: it must remember the number of bits (i.e. how many 0s at the left)
    whenever something is added, increment num_bits

    -> when you write to file, ouput as byte object

    note: this class does not support iterator. use getitem instead

    note: instead of shifting multiple times do floor division (more efficient)
    """

    def __init__(self, num: int, n_bits: int) -> None:
        self.num = num
        self.n_bits = n_bits

    def __getitem__(self, item):
        """
        note: we assume that bitshiftting is a constant operation (in reality it depends
        on cpu; however, the below operations can easily be replaced by floor divisions and mod operations which are constant anyways)
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

    def get_as_byte(self):
        num_bytes = (self.n_bits + 7) // 8
        byte_str = self.num.to_bytes(num_bytes, byteorder='big')
        return bytes(byte_str)

    def __str__(self):
        return bin(self.num).zfill(self.n_bits)