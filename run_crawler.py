from Downloader import Downloader

if __name__ == "__main__":
    url = input("URL to crawl: ")
    if not url.startswith("http://") or not url.startswith("https://"):
        url = "http://" + url
    limit = input("Crawl limit (max=10000): ")
    if int(limit) > 10000:
        limit = 10000
    downloader = Downloader(url)
    downloader.run_downloader(int(limit))