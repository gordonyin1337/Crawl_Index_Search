from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from bs4 import BeautifulSoup
import json
from collections import Counter

WEBPAGES_FOLDER = "C:/Users/Gordon Yin/PycharmProjects/WebCrawler/Pages/"


def _tokenize(data):
    result = []
    stop_words = set(stopwords.words('english'))
    tokenizer = RegexpTokenizer(r"[^_\W]+")
    tokens = tokenizer.tokenize(data)
    for word in tokens:
        if word.lower() not in stop_words:
            result.append(word.lower())
    return result


def tokenize_html(htmldata):
    soup = BeautifulSoup(htmldata, 'lxml')
    for script in soup(["script", "style", "meta", '[document]']):
        script.extract()
    text = soup.get_text()
    return _tokenize(text)


def count_tokens(token_list):
    counts = Counter(token_list)
    return counts.most_common()


def get_filepaths(jsonfile):
    result = []
    data = open(jsonfile)
    for key, value in json.load(data).items():
        result.append(str(key))
    return result


def get_html_data(filepath):
    htmldata = open(WEBPAGES_FOLDER + filepath, 'r')
    return htmldata