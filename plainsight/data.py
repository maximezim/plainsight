import re
from bitstring import ConstBitStream

def to_words(text):
    return text.split()

def take_char_input(stream):
    return stream.read()

def take_binary_input(stream):
    return ConstBitStream(bytes=stream.read())

def to_phrases(order, words):
    return [tuple([words[i+j] for j in range(order+1)])
            for i in range(len(words) - order)]


