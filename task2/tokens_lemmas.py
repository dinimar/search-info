import re
import string
import zipfile
import ssl
import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

morph = pymorphy2.MorphAnalyzer()


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


def write_tokenization_result(result):
    index_txt = open("tokens.txt", "w")
    pattern = "%s\n"
    for word in result:
        index_txt.write(pattern % word)
    index_txt.close()


def get_lemma(word):
    p = morph.parse(word)[0]
    if p.normalized.is_known:
        normal_form = p.normal_form
    else:
        normal_form = word.lower()
    return normal_form


def lemmatization(tokenization_result):
    lemmatization_map = dict()
    for word in tokenization_result:
        normal_form = get_lemma(word)
        if not normal_form in lemmatization_map:
            lemmatization_map[normal_form] = []
        lemmatization_map[normal_form].append(word)
    return lemmatization_map


def write_lemmatization_result(lemmatization_result):
    file = open("lemmas.txt", "w")
    for lemma, tokens in lemmatization_result.items():
        file_string = lemma + " "
        for token in tokens:
            file_string += token + " "
        file_string += "\n"
        file.write(file_string)
    file.close()


def read_file(archive, file_name):
    html = archive.open(file_name)
    return html


if __name__ == '__main__':
    ssl._create_default_https_context = ssl._create_unverified_context
    nltk.download('stopwords')
    archive = zipfile.ZipFile('../task1/files.zip', 'r')
    tokenization_result = set()
    for file in archive.filelist:
        current_html_file = read_file(archive, file.filename)
        current_file_tokenization_result = set(tokenization(current_html_file))
        tokenization_result = tokenization_result | current_file_tokenization_result
        print("tokenization for", file.filename, "finished")
    write_tokenization_result(tokenization_result)
    lemmatization_result = lemmatization(tokenization_result)
    write_lemmatization_result(lemmatization_result)
