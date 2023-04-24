
class Encoder:
    def __init__(self):
        pass

    def transform(self, text: str) -> int:
        encoded_text = self._huffman_encode(self._bwt_encode(text))

    def _bwt_encode(self):
        pass

    def _huffman_encode(self):
        pass

    def _elias_encode(self):
        pass

class Decoder:
    pass

if __name__ == "__main__":
    text = "test_text"
    encoder = Encoder()
    encoded_text = encoder.transform(text)

    decoder = Decoder()
    original_text = decoder.transform(encoded_text)


