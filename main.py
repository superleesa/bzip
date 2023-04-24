from elias import elias_encode, elias_decode, decimal_to_bitarray

encoded = elias_encode(561)
print(encoded)
# print(decimal_to_bitarray(112))

print(elias_decode(encoded))