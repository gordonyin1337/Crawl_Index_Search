import sqlite3
import json
from nltk.corpus import stopwords
import tokenizer
from collections import defaultdict
from scipy import spatial
import string

BOOKKEEPING = "C:/Users/Gordon Yin/PycharmProjects/WebCrawler/Pages/bookkeeping.json"


def retrieve_info(query, cursor):
    cursor.execute('SELECT * FROM InvertedIndex WHERE term=?', (query,))
    result = cursor.fetchone()
    if result:
        info = result[1]
        return info
    else:
        return None


def return_document(infostr):
    return infostr[0:infostr.find('-')]


def return_tfidf(infostr):
    tfidf_score = infostr[infostr.find('-')+1:len(infostr)]
    return float(tfidf_score)


def return_sorted_references(infostr):
    result = []
    sorted_list = sorted(infostr.split(';'), key=return_tfidf, reverse=True)
    for item in sorted_list:
        result.append(item[0:item.find('-')])
    return result


def return_sorted_info(infostr):
    result = []
    sorted_list = sorted(infostr.split(';'),key=return_tfidf,reverse=True)
    return sorted_list


def return_links(filepath):
    data = open(BOOKKEEPING)
    for key, value in json.load(data).items():
        if key == filepath:
            return value


def return_pairs(infostr):
    result = []
    for item in infostr.split(';'):
        result.append((return_document(item),return_tfidf(item)))
    return result


def return_query_tfidf(query, idf_dict):
    tfidf_list = []
    stop_words = set(stopwords.words('english'))
    for word in tokenizer.count_tokens((query.split())):
        if word[0] in idf_dict and word[0] not in stop_words:
            idf = idf_dict[word[0]]
        elif word[0] in stop_words:
            continue
        else:
            idf = 0
        tf = float(word[1])/float(len(set(query.split())))
        tfidf = idf*tf
        tfidf_list.append(tfidf)
    return tfidf_list


def run_search_engine(user_input):
    result_list = []
    translator = str.maketrans("","", string.punctuation)
    user_input = user_input.translate(translator)

    connection = sqlite3.connect('InvertedIndex.db')
    connection_cursor = connection.cursor()

    connection2 = sqlite3.connect('idfs.db')
    connection_cursor2 = connection2.cursor()

    tfidf_dict = dict()
    for word in set(user_input.split()):
        try:
            connection_cursor2.execute('SELECT * FROM idfs WHERE term=?', (word.lower(),))
            item = connection_cursor2.fetchone()
            tfidf_dict[item[0]] = item[1]
        except TypeError:
            continue

    if len(user_input.split()) > 1:
        info_list = []
        info_dict_list = []
        stop_words = set(stopwords.words('english'))

        for word in set(user_input.split()):
            if word.lower() not in stop_words:
                info = retrieve_info(word.lower(), connection_cursor)
                if info:
                    info_list.append(set(return_sorted_references(info)[0:20]))
                    info_dict_list.append((word.lower(),dict(return_pairs(info))))
                else:
                    return []

        common_docs = set.intersection(*info_list)
        if len(common_docs) < 10:
            common_docs = common_docs.union(*info_list)

        common_doc_info = defaultdict(list)
        for doc in common_docs:
            for dic in info_dict_list:
                for key, value in dic[1].items():
                    if doc == key:
                        common_doc_info[doc].append(value)

        cosine_list = []
        for ref, value in common_doc_info.items():
            query_idf = return_query_tfidf(user_input.lower(), tfidf_dict)
            if len(value) == len(query_idf) - 1:
                new_value = value + [0]
                cosine_list.append((ref, 1-spatial.distance.cosine(query_idf,new_value)))
            elif len(value) == len(query_idf):
                cosine_list.append((ref, 1 - spatial.distance.cosine(query_idf, value)))
            else:
                continue

        for pair in sorted(cosine_list, key= lambda x: x[1], reverse=True)[0:10]:
            result_list.append(return_links(pair[0]))

    else:
        info = retrieve_info(user_input.lower(), connection_cursor)
        if info:
            for ref in return_sorted_references(info)[0:10]:
                result_list.append(return_links(ref))

    return result_list


if __name__ == '__main__':
    query = input("Enter search query: ")
    print ('''\nSearch results for "%s": ''' % query)
    link_list = run_search_engine(query)
    if link_list:
        for link in link_list:
            print (link.split(';')[1])
    else:
        print ("No Results")
