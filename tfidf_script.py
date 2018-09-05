import math
import tokenizer
import sqlite3



# File path of Bookkeeping JSON
BOOKKEEPING_JSON = "C:/Users/Gordon Yin/PycharmProjects/WebCrawler/Pages/bookkeeping.json"

# Total Number of Files
N = 180

# Dict to store token and document frequency
token_frequency = {}


def calculate_idf(frequency):
    return math.log10((N/frequency))


def update_frequency_dict(tokens, fr_dict):
    for token in tokens:
        if token not in fr_dict:
            fr_dict[token] = 1
        else:
            fr_dict[token] += 1


def run_idf_script():
    conn = sqlite3.connect("idfs.db")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE idfs (term text, idf real)")
    filepaths = tokenizer.get_filepaths(BOOKKEEPING_JSON)
    print ("Finished set up, going into path loop")
    counter = 0
    for path in filepaths:
        data = tokenizer.get_html_data(path)
        counter += 1
        print ("Got token data from path:", path, counter)
        tokens = set(tokenizer.tokenize_html(data))
        update_frequency_dict(tokens, token_frequency)

    print ("Made frequency dict, gonna update DB")

    for key, value in token_frequency.items():
        idf = calculate_idf(value)
        cursor.execute("INSERT INTO idfs VALUES (?,?)", (key, idf))

    conn.commit()
    conn.close()
    print ("Done!")
