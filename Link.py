import urllib.request
import urllib.error
import urllib.parse
import urllib.robotparser
from bs4 import BeautifulSoup
import requests

class Link:

    def __init__(self, url):
        self.url = create_url(url)
        self.final_url = create_url(url)
        self.index_data = {}
        self.is_redirected = False
        self.html_data = None

    def download_html(self):
        self.check_for_redirect()
        self.html_data = urllib.request.urlopen(str(self.url)).read()
        self.create_index_data()
        return

    def check_for_redirect(self):
        response_object = urllib.request.urlopen(str(self.url))
        if response_object.geturl() != self.url or response_object.getcode() in [300, 301, 302, 303, 307]:
            self.is_redirected = True
            self.final_url = create_url(response_object.geturl())
        return

    def create_index_data(self):
        soup = BeautifulSoup(self.html_data, 'lxml')
        site_title = soup.title
        if site_title:
            self.index_data = (site_title.string, self.final_url)
        else:
            self.index_data = (self.final_url, self.final_url)
        return

    def get_url_info(self):
        parsed_info = urllib.parse.urlparse(self.final_url)
        return parsed_info


def create_url(url):
    fixed_url = url
    try:
        url.encode('ascii')
    except UnicodeEncodeError:
        parsed_url = urllib.parse.urlparse(url)
        fixed_path = urllib.parse.quote(parsed_url.path)
        fixed_url = urllib.parse.urljoin(url, fixed_path)
    finally:
        return fixed_url

