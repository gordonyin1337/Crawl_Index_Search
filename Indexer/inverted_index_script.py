from Indexer import tokenizer, tfidf_script
import sqlite3
import math


def build_database():
    connection = sqlite3.connect("InvertedIndex.db")
    c = connection.cursor()
    c.execute("CREATE TABLE InvertedIndex (term text, info text)")
    connection.commit()
    connection.close()


def calculate_tf(term_count):
    count = float(term_count)
    return 1 + math.log10(count)


def calculate_idf(doc_total, term_count):
    return math.log(doc_total/term_count)


def add_to_dict(term, document, info, dictionary):
    if term not in dictionary:
        term_info = str(document) + "-" + str(info)
        dictionary[term] = term_info
    else:
        term_info = ";" + str(document) + "-" + str(info)
        dictionary[term] += term_info


def run_inverted_index_script(bookkeeping):
    build_database()

    connection = sqlite3.connect("InvertedIndex.db")
    c1 = connection.cursor()

    connection2 = sqlite3.connect("idfs.db")
    c2 = connection2.cursor()

    c2.execute("SELECT * FROM idfs")
    idf_dict = dict(c2.fetchall())

    found_words = dict()

    file_paths = tokenizer.get_filepaths(bookkeeping)

    print("Beginning Inverted Index Construction\n")
    print("Building Inverted Index Dictionary")
    counter = 0
    for path in file_paths:
        data = tokenizer.get_html_data(path)
        tokens = tokenizer.tokenize_html(data)
        token_counts = tokenizer.count_tokens(tokens)
        counter += 1
        for token in token_counts:
            tf = calculate_tf(token[1])
            idf = idf_dict[token[0]]
            tfidf = str(tf*idf)
            add_to_dict(token[0], path, tfidf, found_words)
        print("Parsed through file: ", path, "Number: ", counter)

    print("Total tokens: ", len(found_words))
    print("Completed Index dictionary. Inserting into db")

    for key, value in found_words.items():
        c1.execute("INSERT INTO InvertedIndex VALUES (?, ?)", (key, value))

    connection.commit()
    connection.close()

    print("Done!")


if __name__ == '__main__':
    bookkeeping = "./Sites" + input("Site title: ")
    print("Building IDF database")
    tfidf_script.run_idf_script(bookkeeping)
    print("Building Inverted Index")
    run_inverted_index_script(bookkeeping)
