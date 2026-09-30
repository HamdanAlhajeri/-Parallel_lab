from mrjob.job import MRJob
class MRAnagrams(MRJob):
    def mapper(self, _, line):
        for word in line.split():
            yield "".join(sorted(word)), word

    def reducer(self, key, words):
        anagrams = sorted(set(words))
        if len(anagrams) > 1:
            yield key, anagrams

if __name__ == "__main__":
    MRAnagrams.run()
