"""Lab 4: Python recap and MapReduce tasks."""

import argparse
import re
from collections import Counter
from functools import reduce
from mrjob.job import MRJob
from mrjob.step import MRStep

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

class LabJob(MRJob):
    def configure_args(self):
        super().configure_args()
        # Forward the selection when MRJob launches mapper/reducer processes.
        self.add_passthru_arg(
            "--task", choices=("3", "4"), default="4",
            help="Lab task to run (default: 4)",
        )


class Task3(LabJob):
    """Find groups of distinct anagrams in the input word list."""

    def mapper(self, _, line):
        word = line.strip()
        if word:
            yield ''.join(sorted(word)), word

    def reducer(self, sorted_letters, words):
        group = sorted(set(words))
        if len(group) > 1:
            yield sorted_letters, group


class Task4(LabJob):

    pass

def Task5():
    """find the highest average rating; break ties by smallest movie ID."""
    
    def steps(self):
        return [
            MRStep(mapper=self.mapper_ratings,
                    combiner=self.combine_ratings,
                    reducer=self.reducer_average),
            MRStep(reducer=self.reducer_highest),
        ]

    def mapper_ratings(self, _, line):
        if not line.strip():
            return
        user_id, movie_id, rating, timestamp = line.split("\t")
        if user_id.lstrip("\ufeff") == "userId":
            return
        yield int(movie_id), (float(rating), 1)

    def combine_ratings(self, movie_id, totals):
        total_score = 0.0
        total_count = 0
        for score, count in totals:
            total_score += score
            total_count += count
        yield movie_id, (total_score, total_count)

    def reducer_average(self, movie_id, totals):
        for _, (total_score, total_count) in self.combine_ratings(movie_id, totals):
            yield None, (total_score / total_count, movie_id)

    def reducer_highest(self, _, movies):
        average, movie_id = max(movies, key=lambda movie: (movie[0], -movie[1]))
        yield movie_id, average

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lab 4: Python recap and MapReduce tasks.")
    parser.add_argument("--task", choices=("1", "2", "3", "4", "5"), required=True,
                        help="Lab task to run (1-5)")
    args = parser.parse_args()

    if args.task == "1":
        Task1()
    elif args.task == "2":
        Task2()
    elif args.task == "3":
        Task3.run()
    elif args.task == "4":
        Task4.run()
    elif args.task == "5":
        Task5.run()
