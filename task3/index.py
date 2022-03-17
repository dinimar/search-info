import re
import zipfile
import nltk
from functools import cmp_to_key

from tokens_lemmas import tokenization, get_lemma


class WordInfo:
    def __init__(self):
        self.documents = []
        self.general_count = 0

    def append_document_info(self, document_number, document_word_count):
        self.documents.append(document_number)
        self.general_count += document_word_count


def read_lemmatization():
    f = open("lemmas.txt", "r")
    lines = f.readlines()
    map = dict()
    for line in lines:
        key = None
        words = re.split('\s+', line)
        for i in range(len(words) - 1):
            if i == 0:
                key = words[i]
                map[key] = []
            else:
                map[key].append(words[i])
    return map


def get_document_index(filename):
    number = ""
    for letter in filename:
        if letter.isdigit():
            number += letter
    return int(number)


def sort_index(index):
    def comparator(x, y):
        return x[1].general_count - y[1].general_count

    return dict(sorted(index.items(), key=cmp_to_key(comparator), reverse=True))


def find_words_in_html_files(map):
    archive = zipfile.ZipFile('files.zip', 'r')
    index = dict()
    i = 0
    for file in archive.filelist:
        html = archive.open(file.filename)
        html_word_list = tokenization(html)
        word_used = set()
        for word in html_word_list:
            lemma = get_lemma(word)
            if lemma in map.keys() and lemma not in word_used:
                word_used.add(lemma)
                similar_words = map[lemma]
                count = 0
                for similar_word in similar_words:
                    count += html_word_list.count(similar_word)
                if lemma not in index.keys():
                    index[lemma] = WordInfo()
                numbers = re.findall(r'\d+', file.filename)
                index[lemma].append_document_info(int(numbers[0]), count)
        print("end of reading doc ", file.filename)
    return dict(sorted(index.items()))


def write_index_generation_result(index):
    file = open("index.txt", "w")
    for word, doc_info in index.items():
        file_string = word + " "
        for doc in doc_info.documents:
            file_string += " " + str(doc)
        file_string += "\n"
        file.write(file_string)
    file.close()


def create_index():
    map = read_lemmatization()
    index = find_words_in_html_files(map)
    sorted_index = sort_index(index)
    write_index_generation_result(sorted_index)


def read_index():
    f = open("index.txt", "r")
    lines = f.readlines()
    map = dict()
    for line in lines:
        words = re.split('\s+', line)
        key = words[0]
        if not key in map.keys():
            map[key] = set()
        for i in range(1, len(words) - 1):
            map[key].add(words[i])
    return map

if __name__ == '__main__':
    nltk.download('stopwords')
    create_index()
