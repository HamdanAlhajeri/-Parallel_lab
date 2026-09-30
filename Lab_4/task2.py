from mrjob.job import MRJob
class MRCounter(MRJob):
    def mapper(self, _, line):
        yield "lines", 1
        yield "characters", len(line)
        yield "words", len(line.split())

    def reducer(self, key, counts):
        yield key, sum(counts)

if __name__ == "__main__":
    MRCounter.run()
