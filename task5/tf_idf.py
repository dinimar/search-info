import re
import string
import zipfile
from math import log

import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

morph = pymorphy2.MorphAnalyzer()

def get_lemma(word):
    p = morph.parse(word)[0]
    if p.normalized.is_known:
        normal_form = p.normal_form
    else:
        normal_form = word.lower()
    return normal_form

def tokenization(html):
    soup = BeautifulSoup(html).get_text()
    tokenization_condition = get_tokenization_condition()
    result = list((filter(tokenization_condition, nltk.wordpunct_tokenize(soup))))
    result = exclude_punctuation(result)
    result = list(filter(exclude_trash(), result))
    result = list(filter(exclude_numeral, result))
    result = list(filter(exclude_not_permitted_symbols, result))
    result = list(filter(exclude_glued_words, result))
    return result


def exclude_numeral(word):
    regex = re.compile(r'^[0-9]+$')
    if bool(regex.match(word.strip())):
        return 1850 < int(word) < 2030
    return True


def exclude_not_permitted_symbols(word):
    russian_words = re.compile(r'^[а-яА-Я]{2,}$')
    english_words = re.compile(r'^[a-zA-Z]{2,}$')
    numbers_words = re.compile(r'^[0-9]+$')
    result = bool(russian_words.match(word)) or bool(english_words.match(word)) or bool(numbers_words.match(word))
    return result


def exclude_glued_words(word):
    if word == word.upper():
        return True
    capitalize_word = word[0].upper() + word[1:]
    split_result = re.findall(r'[А-ЯA-Z][^А-ЯA-Z]*', capitalize_word)
    one_len_word_count = len(list(filter(lambda element: len(element) == 1, split_result)))
    result = len(split_result) < 2 or one_len_word_count > 0
    return result


def exclude_trash():
    trash = ['«', '»', '→', '·', '®', '▼', '–', '▸', 'x', 'X', ' ']
    return lambda word: word not in trash


def exclude_punctuation(values):
    return [i for i in values if all(not j in string.punctuation for j in i)]


def get_tokenization_condition():
    stop_words = stopwords.words('russian')
    stop_words.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на', 'o'])
    return lambda word: word not in stop_words


def read_tokens():
    f = open("../task3/lemmas.txt", "r")
    lines = f.readlines()
    tokens = set()
    for line in lines:
        words = re.split('\s+', line)
        tokens.add(words[0])
    return tokens


def read_index():
    f = open("../task3/index.txt", "r")
    lines = f.readlines()
    index = dict()
    for line in lines:
        words = re.split('\s+', line)
        index[words[0]] = []
        for i in range(1, len(words) - 1):
            index[words[0]].append(words[i])
    for key, value in index.items():
        index[key] = set(value)
    return index


def read_tf():
    f = open("tf.txt", "r")
    lines = f.readlines()
    tf_map = dict()
    for line in lines:
        words = re.split('\s+', line)
        key = words[0]
        for i in range(1, len(words) - 2, 2):
            if key not in tf_map:
                tf_map[key] = []
            tf_map[key].append((words[i], words[i + 1]))
    return tf_map


def read_idf(path):
    f = open(path, "r")
    lines = f.readlines()
    idf_map = dict()
    for line in lines:
        words = re.split('\s+', line)
        idf_map[words[0]] = words[1]
    return idf_map


def write_tf(tf_map):
    file = open("tf.txt", "w")
    for word, tf_list in tf_map.items():
        file_string = word + " "
        for tf in tf_list:
            file_string += " " + tf[0] + " " + str(tf[1])
        file_string += "\n"
        file.write(file_string)
    file.close()


def write_idf(idf_map):
    file = open("idf.txt", "w")
    for word, idf in idf_map.items():
        file_string = word + " " + str(idf)
        file_string += "\n"
        file.write(file_string)
    file.close()


def write_tf_idf(tf_idf_map):
    file = open("tf_idf.txt", "w")
    for word, tf_idf_list in tf_idf_map.items():
        file_string = word + " "
        for tf in tf_idf_list:
            file_string += " " + tf[0] + " " + str(tf[1])
        file_string += "\n"
        file.write(file_string)
    file.close()


def tf_calculate():
    archive = zipfile.ZipFile('../task3/files.zip', 'r')
    tf_map = dict()
    for file in archive.filelist:
        numbers = re.findall(r'\d+', file.filename)
        file_num = 0
        if len(numbers) > 0:
            file_num = numbers[0]
        tf_page_map = dict()
        html = archive.open(file.filename)
        html_word_list = tokenization(html)
        for word in html_word_list:
            lemma = get_lemma(word)
            if lemma in tf_page_map.keys():
                tf_page_map[lemma] += 1
            else:
                tf_page_map[lemma] = 1
        for key, value in tf_page_map.items():
            if key not in tf_map.keys():
                tf_map[key] = []
            tf = round(value / len(html_word_list), 6)
            tf_map[key].append((file_num, tf))
        print("read tf for", file.filename)
    return tf_map


def idf_calculate():
    archive = zipfile.ZipFile('../task3/files.zip', 'r')
    documents_number = len(archive.filelist)
    token_document_map = dict()
    index = read_index()
    for element, pages in index.items():
        token_document_map[element] = round(log(documents_number / len(pages)), 6)
    return token_document_map
import ntpath
from pathlib import Path

def tf_idf_calculate():
    archive = zipfile.ZipFile('../task3/files.zip', 'r')
    html_files = archive.namelist()
    tf_data = dict(sorted(read_tf().items()))
    idf_data = dict(sorted(read_idf("idf.txt").items()))
    tf_idf_map = dict()
    for token, documents_tf in tf_data.items():
        tf_idf_map[token] = []
        documents_tf = dict(documents_tf)
        for document in html_files:
            name = Path(document).stem
            if name in documents_tf.keys():
                tf = float(documents_tf[name])
            else:
                tf = float(0)
            tf_idf_map[token].append((name, tf * float(idf_data[token])))
    return tf_idf_map


if __name__ == '__main__':
    # tf_result = tf_calculate()
    # write_tf(tf_result)
    # idf_result = idf_calculate()
    # write_idf(idf_result)
    tf_idf_result = tf_idf_calculate()
    write_tf_idf(tf_idf_result)
