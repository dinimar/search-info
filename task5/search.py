import re
import zipfile
from math import sqrt

from bs4 import BeautifulSoup

from tokens_lemmas import tokenization, get_lemma
from index_and_boolean_search import boolean_search, read_index
from tf_idf import read_idf




def read_file(archive, file_name):
    html = archive.open(file_name)
    return html


def read_html_pages():
    archive = zipfile.ZipFile('../task1/files.zip', 'r')
    pages_with_title = dict()
    for file in archive.filelist:
        if (file.filename != 'files/'):
            current_html_file = read_file(archive, file.filename)
            soup = BeautifulSoup(current_html_file)
            pages_with_title[file.filename] = soup.title.string
    return pages_with_title


def read_tf_idf():
    f = open("../task4/tf_idf.txt", "r")
    lines = f.readlines()
    tf_idf_map = dict()
    for line in lines:
        words = re.split('\s+', line)
        key = words[0]
        for i in range(1, len(words) - 2, 2):
            if key not in tf_idf_map:
                tf_idf_map[key] = []
            tf_idf_map[key].append((words[i], words[i + 1]))
    return tf_idf_map


def read_html():
    f = open("../task1/index.txt", "r")
    lines = f.readlines()
    htmls = dict()
    for line in lines:
        words = re.split('\s+', line)
        key = "page" + words[0] + "html"
        htmls[key] = words[1]
    return htmls


def calculate_tf_idf_query(query_words, index, idf):
    query_vector = dict()
    for word in query_words:
        query_frequency = 0
        for inner_word in query_words:
            if word == inner_word:
                query_frequency += 1
        tf = query_frequency / len(query_words)
        if word not in idf.keys():
            query_vector[word] = 0
        else:
            query_vector[word] = float(idf[word]) * tf
    return query_vector


def calculate_pages_tf_idf(pages, query_words, tf_idf_data):
    result = dict()
    for word in set(query_words):
        not_found = True
        if word in tf_idf_data.keys():
            not_found = False
            word_tf_idf = dict(tf_idf_data[word])
        for page in pages:
            if page not in result.keys():
                result[page] = []
            if not_found:
                tf_idf = 0
            else:
                tf_idf = word_tf_idf[page]
            result[page].append((word, tf_idf))
    return result


def ranging_vectors(query_tf_idf, pages_tf_idf):
    def calculate_vector_length(vector):
        return sqrt(sum(list(map(lambda x: float(x) * float(x), vector.values()))))

    def calculate_similarity(length_query, length_vector, numerator):
        return numerator / (length_vector * length_query)

    pages_cos = dict()
    query_vector_length = calculate_vector_length(query_tf_idf)
    for page, tf_idf_words in pages_tf_idf.items():
        tf_idf_words = dict(tf_idf_words)
        vector_length = calculate_vector_length(tf_idf_words)
        numerator = 0
        for word, tf_idf in tf_idf_words.items():
            numerator += float(tf_idf) * float(query_tf_idf[word])
        if numerator == 0:
            pages_cos[page] = 0
        pages_cos[page] = calculate_similarity(query_vector_length, vector_length, numerator)

    pages_cos = dict(sorted(pages_cos.items(), key=lambda item: item[1], reverse=True))
    return pages_cos

def search_with_ranging_tf_idf(query):
    htmls = read_html()
    index = read_index("../task3/index.txt")
    tf_idf = read_tf_idf()

    query_words = tokenization(query)
    query_words = list(map(lambda word: get_lemma(word), query_words))
    boolean_search_query = " | ".join(query_words)
    pages = boolean_search(boolean_search_query, index)
    pages_tf_idf = calculate_pages_tf_idf(pages, query_words, tf_idf)

    result = dict()
    for page, tf_idf_words in pages_tf_idf.items():
        sum = 0
        tf_idf_words = dict(tf_idf_words)
        for word, tf_idf in tf_idf_words.items():
            sum += float(tf_idf)
        result[page] = sum
    result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

    search_result = dict()
    pages_with_title = read_html_pages()

    i = 0
    for key in list(result.keys()):
        if result[key] >= 1:
            continue
        i += 1
        search_result[key] = result[key]
        if i == 5:
            break
    result = dict()
    for page in search_result.keys():
        print(htmls['page' + page + 'html'])
        result[htmls['page' + page + 'html']] = pages_with_title['files/' + page + '.txt']
    print("Search finished")
    return result



def search_page(query):
    htmls = read_html()
    index = read_index()
    idf = read_idf("../task4/idf.txt")
    tf_idf = read_tf_idf()
    print("read all data")

    query_words = tokenization(query)
    query_words = list(map(lambda word: get_lemma(word), query_words))
    boolean_search_query = " | ".join(query_words)
    pages = boolean_search(boolean_search_query, index)
    query_tf_idf = calculate_tf_idf_query(query_words, index, idf)
    pages_tf_idf = calculate_pages_tf_idf(pages, query_words, tf_idf)
    ranging_result = ranging_vectors(query_tf_idf, pages_tf_idf)
    search_result = dict()
    pages_with_title = read_html_pages()

    print('ranging_result:', ranging_result)

    i = 0
    for key in list(ranging_result.keys()):
        if ranging_result[key] >= 1:
            continue
        i += 1
        search_result[key] = ranging_result[key]
        if i == 5:
            break
    result = dict()
    for page in search_result.keys():
        print(htmls[page])
        result[htmls[page]] = pages_with_title[page]
    print("Search finished")
    return result

if __name__ == '__main__':
    query = input('Введите ваш запрос: ')
    result = search_page(query)

    print(result)