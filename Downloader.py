from Link import Link
import queue
import urllib.request
import urllib.error
import urllib.parse
import urllib.robotparser
import re
from bs4 import BeautifulSoup
import json
import time
import requests
import os.path


class Downloader:
    def __init__(self, initial_url):
        self.initial_url = initial_url
        self.visited = {}
        self.unprocessed_links = queue.Queue()
        self.counter = 0
        self.has_robot = True
        self.robot_url = ''
        self.counter = 0
        self.bookkeeping_data = {}
        self.crawl_delay = 5

    def add_links_to_queue(self, link_object):
        for link in extract_next_links(link_object):
            self.unprocessed_links.put(link)
        return

    def download_link(self, link_object):
        try:
            link_object.download_html()
            self.visited[link_object.get_url_info().path] = 1
        except urllib.error.HTTPError:
            self.visited[link_object.get_url_info().path] = 1
            raise
        return

    def write_to_file(self, link_object):
        parse_info = urllib.parse.urlparse(self.initial_url)
        folder_path = "./Sites/" + parse_info.hostname
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_object = open(folder_path + '/' + str(self.counter), 'w')
        file_object.write(str(link_object.html_data))
        file_object.close()
        self.bookkeeping_data[self.counter] = str(link_object.index_data[0]) + ";" + str(link_object.index_data[1])
        self.counter += 1
        return

    def check_robot(self, url):
        if self.has_robot:
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(self.robot_url)
            rp.read()
            return rp.can_fetch('*', url)
        else:
            return True

    def robot_exists(self):
        parse_info = urllib.parse.urlparse(self.initial_url)
        self.robot_url = parse_info.scheme + "://" + parse_info.hostname + "/robots.txt"
        try:
            urllib.request.urlopen(self.robot_url)
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(self.robot_url)
            rp.read()
            if rp.request_rate('*') is not None:
                self.crawl_delay = int(rp.request_rate('*').seconds // rp.request_rate('*').requests)
            if rp.crawl_delay('*') is not None:
                self.crawl_delay = rp.crawl_delay('*')
        except urllib.error.HTTPError:
            self.has_robot = False
        return

    def build_json(self):
        parse_info = urllib.parse.urlparse(self.initial_url)
        filepath = "./Sites/" + parse_info.hostname
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.bookkeeping_data, f)

    def initialize(self):
        initial_link = Link(self.initial_url)
        try:
            if is_valid(self.initial_url):
                print("Initializing Crawler for URL: " + initial_link.final_url)
                print("Crawl Delay: " + str(self.crawl_delay))
                self.download_link(initial_link)
                self.initial_url = initial_link.final_url
                self.robot_exists()
                self.add_links_to_queue(initial_link)
                self.write_to_file(initial_link)
                print("Done! Beginning Crawl...")
        except urllib.error.HTTPError:
            print("Link Error!")

    def run_downloader(self, limit):
        self.initialize()
        try:
            while self.unprocessed_links.qsize() > 0 and self.counter <= limit:
                new_url = self.unprocessed_links.get()
                new_link = Link(new_url)
                initial_domain = urllib.parse.urlparse(self.initial_url).hostname
                if is_valid(new_url, initial_domain.strip("www.")) and self.check_robot(new_url) \
                        and new_link.get_url_info().path not in self.visited:
                    time.sleep(self.crawl_delay)
                    print("Downloading URL #" + str(self.counter) + ":" + new_link.final_url)
                    try:
                        self.download_link(new_link)
                        self.add_links_to_queue(new_link)
                        self.write_to_file(new_link)
                    except urllib.error.HTTPError:
                        print("Download Failed!")
                        continue
                    except TimeoutError:
                        print("Timout Error!")
                        continue
        except KeyboardInterrupt:
            print("Canceled Early!")
        finally:
            self.shutdown()

    def shutdown(self):
        print("Building bookkeeping.json...")
        self.build_json()
        print("Crawler Finished!")
        return


def extract_next_links(link_object):
    outputLinks = []
    soup = BeautifulSoup(link_object.html_data, 'lxml')

    try:
        for link in soup.find_all('a'):
            if link_object.is_redirected:
                outputLinks.append(urllib.parse.urljoin(link_object.final_url, link.get('href')))
            else:
                outputLinks.append(urllib.parse.urljoin(link_object.url, link.get('href')))

        return outputLinks
    except:
        return []


def is_valid(url, domain=None):
    parsed_info = urllib.parse.urlparse(url)
    if parsed_info.scheme not in ['http', 'https']:
        return False
    elif domain is not None and domain not in parsed_info.hostname:
        return False
    elif parsed_info.fragment != '':
        return False
    elif check_request_code(url) > 400:
        return False
    try:
        return not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                 + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                 + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                 + "|thmx|mso|arff|rtf|jar|csv" \
                 + "|rm|smil|wmv|swf|wma|zip|rar|gz|pdf)$", parsed_info.path.lower())
    except TypeError:
        return False


def check_request_code(url):
    r = requests.head(url)
    return r.status_code
