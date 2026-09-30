"""Lab 4, Task 1: Python recap for MapReduce."""

import re
from collections import Counter
from functools import reduce

def Task1():
    def tokenize(input_string):
        return re.findall(r'\w+', input_string.lower())


    def my_generator(n):
        value = 0
        while value < n:
            yield value
            value += 1

    print("1. map")
    numbers = [1, 2, 3, 4, 5]
    duplicate = list(map(lambda x: 2 * x, numbers))
    print(duplicate)

    print("\n2. reduce")
    product = reduce(lambda x, y: x * y, numbers)
    print(product)

    print("\n3. Tokenization")
    input_string = "This is a sample string and contains 11 words."
    words = tokenize(input_string)
    print(words)
    print(len(words))

    print("\n4. Generator")
    for value in my_generator(5):
        print(value)

    print("\n5. Counter")
    input_string = "This is a sample string and contains sample words."
    word_list = re.findall(r'\b[a-zA-Z]+\b', input_string.lower())
    word_frequencies = Counter(word_list)
    print(word_frequencies)

def Task2():

    pass

def Task3():
    pass

def Task4():
    pass

def Task5():
    pass

if __name__ == "__main__":
    Task1()
