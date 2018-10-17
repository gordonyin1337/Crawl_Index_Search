# Summer_Project_1
A web crawler console application that downloads html data from webpages under a single domain up to a limit of 10000 pages. The application stores html data locally in a directory with a bookkeeping json that stores the link and title of the page crawled.

The Indexer directory contains an inverted index script that calculates each page's TF-IDF and stores the data in a SQL database. The search application uses both a normalized tf-idf rating as well as cosine spatial similarity to return the top pages of a search query.
