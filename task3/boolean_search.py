import re


def read_index(index_file):
    f = open(index_file, "r")
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


def boolean_search(query, index):
    and_operator = '&'
    or_operator = '|'
    not_operator = 'not'

    all_pages = set()
    for page in index.values():
        all_pages = all_pages | page

    def and_operation(set_a, set_b):
        return set_a & set_b

    def or_operation(set_a, set_b):
        return set_a | set_b

    def difference_set(set_a, set_b):
        return set_a - set_b

    words = re.split('\s+', query)
    inversion = False

    query_in_sets = []

    prev_set = set()
    for i in range(len(words)):
        word = words[i]
        if i == len(words) - 1:
            if word not in index.keys():
                prev_set = set()
            elif inversion:
                prev_set = difference_set(all_pages, index[word])
            else:
                prev_set = index[word]
            query_in_sets.append((prev_set, None))
        if word == and_operator or word == or_operator:
            query_in_sets.append((prev_set, word))
            continue

        if word == not_operator:
            inversion = True
            continue
        if word not in index.keys():
            prev_set = set()
        elif inversion:
            prev_set = difference_set(all_pages, index[word])
            inversion = False
        else:
            if word not in index.keys():
                prev_set = set()
            else:
                prev_set = index[word]

    def run_operations(query, operation_symbol, operation_func):
        result = []
        for i in range(len(query) - 1):
            if query[i][1] == operation_symbol:
                current_result = operation_func(query[i][0], query[i + 1][0])
                query[i + 1] = (current_result, query[i + 1][1])
            else:
                result.append((query[i][0], query[i][1]))
        result.append((query[len(query) - 1]))
        return result

    and_result = run_operations(query_in_sets, and_operator, and_operation)
    or_result = run_operations(and_result, or_operator, or_operation)
    if len(or_result) == 1:
        print("Correct query")
    return or_result[0][0]


if __name__ == '__main__':
    index = read_index("index.txt")
    result = boolean_search("Яндекс", index)
    print(len(result))
    result = list(map(lambda x: x[4:6], result))
    print(result)